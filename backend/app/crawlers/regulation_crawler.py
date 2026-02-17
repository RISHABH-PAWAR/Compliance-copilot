"""Regulatory Crawler - Government Gazette Monitor"""
import httpx
from datetime import datetime
from app.core.logging import get_logger

logger = get_logger("regulation_crawler")

SOURCES = [
    {"name": "India Code", "url": "https://www.indiacode.nic.in", "type": "central"},
    {"name": "Maharashtra Labour", "url": "https://mahakamgar.maharashtra.gov.in", "type": "state", "state": "MH"},
    {"name": "Karnataka Labour", "url": "https://labour.karnataka.gov.in", "type": "state", "state": "KA"},
    {"name": "Gujarat Labour", "url": "https://labour.gujarat.gov.in", "type": "state", "state": "GJ"},
    {"name": "Tamil Nadu Labour", "url": "https://www.tn.gov.in/labour", "type": "state", "state": "TN"},
    {"name": "EPFO", "url": "https://www.epfindia.gov.in", "type": "central"},
    {"name": "ESIC", "url": "https://www.esic.nic.in", "type": "central"},
]


class RegulationCrawler:
    """Monitor government websites for labor law updates"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)

    async def check_for_updates(self):
        """Check all sources for updates"""
        updates = []
        for source in SOURCES:
            try:
                result = await self._check_source(source)
                if result:
                    updates.append(result)
            except Exception as e:
                logger.error("crawl_failed", source=source["name"], error=str(e))
        return updates

    async def _check_source(self, source: dict) -> dict:
        """Check a single source for updates"""
        try:
            response = await self.client.get(source["url"])
            if response.status_code == 200:
                logger.info("source_checked", source=source["name"], status="ok")
                return {"source": source["name"], "status": "checked", "timestamp": datetime.utcnow().isoformat()}
        except Exception as e:
            logger.warning("source_unreachable", source=source["name"])
        return None

    async def close(self):
        await self.client.aclose()
