"""Policy Service"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session


class PolicyService:
    """Manages company policy documents via MongoDB"""

    def __init__(self, db: Session):
        self.db = db
        self._mongo_client = None

    @property
    def mongo_db(self):
        from app.config import get_settings
        settings = get_settings()
        
        if self._mongo_client is not None:
            return self._mongo_client[settings.MONGODB_DATABASE]
            
        try:
            from pymongo import MongoClient
            client = MongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=2000)
            # Test connection
            client.server_info()
            self._mongo_client = client
            return client[settings.MONGODB_DATABASE]
        except Exception:
            return None

    def _get_json_db_path(self):
        import os
        from app.config import get_settings
        settings = get_settings()
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        return os.path.join(settings.UPLOAD_DIR, "policies.json")

    def _save_to_json(self, doc: dict):
        import json
        import os
        path = self._get_json_db_path()
        data = []
        if os.path.exists(path):
            with open(path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        
        data.append(doc)
        with open(path, "w") as f:
            json.dump(data, f, default=str, indent=2)

    def _load_from_json(self, company_id: int) -> List[dict]:
        import json
        import os
        path = self._get_json_db_path()
        if not os.path.exists(path):
            return []
        
        with open(path, "r") as f:
            try:
                data = json.load(f)
                return [d for d in data if d.get("company_id") == company_id]
            except json.JSONDecodeError:
                return []

    def upload_policy(
        self,
        company_id: int,
        filename: str,
        policy_type: str,
        raw_text: str,
        state: str = "all",
        file_size: int = 0,
        file_type: str = "pdf",
        uploaded_by: Optional[int] = None,
        tags: List[str] = [],
    ) -> dict:
        from app.models.mongo.policy_document import PolicyDocument

        # Deduplication: Find if a policy with same name exists for this company
        existing_policies = self.get_policies(company_id)["policies"]
        for p in existing_policies:
            if p.get("filename") == filename:
                self.delete_policy(company_id, p["id"])

        doc = PolicyDocument.create(
            company_id=company_id,
            filename=filename,
            policy_type=policy_type,
            state=state,
            raw_text=raw_text,
            file_size=file_size,
            file_type=file_type,
            uploaded_by=uploaded_by,
            tags=tags,
            status="processed",
        )

        if self.mongo_db is not None:
            from app.models.mongo.policy_document import PolicyDocument
            result = self.mongo_db[PolicyDocument.COLLECTION].insert_one(doc)
            doc["id"] = str(result.inserted_id)
            doc.pop("_id", None)
        else:
            # Persistent fallback
            doc["id"] = f"poly_{int(datetime.utcnow().timestamp())}"
            self._save_to_json(doc)
        
        # Trigger Ingestion & Analysis
        try:
            self._ingest_policy(company_id, doc["id"], raw_text, filename)
            from app.services.compliance_service import ComplianceService
            compliance = ComplianceService(self.db)
            compliance.analyze_company_compliance(company_id)
        except Exception as e:
            # Log but don't fail the upload
            import logging
            logging.error(f"Post-upload processing failed: {e}")
            
        return doc

    def delete_policy(self, company_id: int, policy_id: str) -> bool:
        """Delete a policy and its associated vector embeddings"""
        success = False
        if self.mongo_db is not None:
            from bson import ObjectId
            from app.models.mongo.policy_document import PolicyDocument
            result = self.mongo_db[PolicyDocument.COLLECTION].delete_one(
                {"_id": ObjectId(policy_id), "company_id": company_id}
            )
            success = result.deleted_count > 0
        else:
            # JSON fallback deletion
            import json
            import os
            path = self._get_json_db_path()
            if os.path.exists(path):
                with open(path, "r") as f:
                    policies = json.load(f)
                new_policies = [p for p in policies if not (p.get("id") == policy_id and p.get("company_id") == company_id)]
                if len(new_policies) < len(policies):
                    with open(path, "w") as f:
                        json.dump(new_policies, f, default=str, indent=2)
                    success = True

        # Delete from Vector Store
        if success:
            try:
                from app.ai.vectorstore import VectorStoreService
                vectorstore = VectorStoreService()
                vectorstore.delete_by_filter(
                    filter_dict={"policy_id": policy_id},
                    namespace=f"company_{company_id}"
                )
            except Exception as e:
                import logging
                logging.error(f"Failed to delete vectors for policy {policy_id}: {e}")
        
        return success

    def _ingest_policy(self, company_id: int, policy_id: str, text: str, filename: str):
        """Chunk, embed, and upsert policy to vector store"""
        from app.utils.text_chunker import chunk_text
        from app.ai.embeddings import get_embeddings
        from app.ai.vectorstore import VectorStoreService
        
        chunks = chunk_text(text)
        embeddings = get_embeddings()
        vectorstore = VectorStoreService()
        
        vectors = []
        for i, chunk in enumerate(chunks):
            vector = embeddings.embed_query(chunk["text"])
            vectors.append({
                "id": f"policy_{policy_id}_{i}",
                "values": vector,
                "metadata": {
                    "company_id": company_id,
                    "policy_id": policy_id,
                    "filename": filename,
                    "text": chunk["text"],
                    "chunk_index": i,
                    "source_type": "policy",
                }
            })
        
        vectorstore.upsert(vectors, namespace=f"company_{company_id}")

    def get_policies(self, company_id: int, page: int = 1, page_size: int = 20) -> dict:
        if self.mongo_db is not None:
            from app.models.mongo.policy_document import PolicyDocument
            collection = self.mongo_db[PolicyDocument.COLLECTION]
            total = collection.count_documents({"company_id": company_id})
            policies = list(
                collection.find({"company_id": company_id})
                .skip((page - 1) * page_size)
                .limit(page_size)
                .sort("created_at", -1)
            )
            for p in policies:
                p["id"] = str(p.pop("_id"))
            return {"policies": policies, "total": total, "page": page, "page_size": page_size}
        
        # fallback to JSON
        policies = self._load_from_json(company_id)
        total = len(policies)
        
        # Simple pagination and sorting for JSON
        policies.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        start = (page - 1) * page_size
        end = start + page_size
        
        return {
            "policies": policies[start:end],
            "total": total,
            "page": page,
            "page_size": page_size
        }

    def update_policy(self, company_id: int, policy_id: str, updates: dict) -> bool:
        """Update policy metadata (e.g., rename)"""
        success = False
        if self.mongo_db is not None:
            from bson import ObjectId
            from app.models.mongo.policy_document import PolicyDocument
            result = self.mongo_db[PolicyDocument.COLLECTION].update_one(
                {"_id": ObjectId(policy_id), "company_id": company_id},
                {"$set": updates}
            )
            success = result.modified_count > 0
        else:
            # JSON fallback update
            import json
            import os
            path = self._get_json_db_path()
            if os.path.exists(path):
                with open(path, "r") as f:
                    policies = json.load(f)
                
                updated = False
                for p in policies:
                    if p.get("id") == policy_id and p.get("company_id") == company_id:
                        p.update(updates)
                        updated = True
                        break
                
                if updated:
                    with open(path, "w") as f:
                        json.dump(policies, f, default=str, indent=2)
                    success = True
        return success

    def get_policy(self, company_id: int, policy_id: str) -> dict:
        if self.mongo_db is not None:
            from bson import ObjectId
            from app.models.mongo.policy_document import PolicyDocument
            doc = self.mongo_db[PolicyDocument.COLLECTION].find_one(
                {"_id": ObjectId(policy_id), "company_id": company_id}
            )
            if doc:
                doc["id"] = str(doc.pop("_id"))
                return doc
        else:
            policies = self._load_from_json(company_id)
            for p in policies:
                if p["id"] == policy_id:
                    return p
        return None

    def _get_mock_policies(self, company_id: int, page: int, page_size: int) -> dict:
        mock_policies = [
            {
                "id": "mock_001",
                "company_id": company_id,
                "filename": "employee_handbook_2025.pdf",
                "original_filename": "employee_handbook_2025.pdf",
                "policy_type": "handbook",
                "state": "maharashtra",
                "version": 1,
                "status": "processed",
                "file_size": 2048576,
                "file_type": "pdf",
                "chunk_count": 45,
                "embedding_status": "completed",
                "tags": ["hr", "general"],
                "created_at": datetime(2025, 1, 15),
                "updated_at": datetime(2025, 1, 15),
            },
            {
                "id": "mock_002",
                "company_id": company_id,
                "filename": "wage_policy_q1_2025.pdf",
                "original_filename": "wage_policy_q1_2025.pdf",
                "policy_type": "wage_policy",
                "state": "maharashtra",
                "version": 2,
                "status": "processed",
                "file_size": 512000,
                "file_type": "pdf",
                "chunk_count": 12,
                "embedding_status": "completed",
                "tags": ["wages", "compensation"],
                "created_at": datetime(2025, 2, 1),
                "updated_at": datetime(2025, 2, 1),
            },
            {
                "id": "mock_003",
                "company_id": company_id,
                "filename": "shift_and_overtime_policy.docx",
                "original_filename": "shift_and_overtime_policy.docx",
                "policy_type": "shift_policy",
                "state": "all",
                "version": 1,
                "status": "processed",
                "file_size": 340000,
                "file_type": "docx",
                "chunk_count": 8,
                "embedding_status": "completed",
                "tags": ["shifts", "overtime", "operations"],
                "created_at": datetime(2025, 1, 20),
                "updated_at": datetime(2025, 1, 20),
            },
            {
                "id": "mock_004",
                "company_id": company_id,
                "filename": "attendance_rules_2025.pdf",
                "original_filename": "attendance_rules_2025.pdf",
                "policy_type": "attendance",
                "state": "all",
                "version": 1,
                "status": "processed",
                "file_size": 180000,
                "file_type": "pdf",
                "chunk_count": 6,
                "embedding_status": "completed",
                "tags": ["attendance", "hr"],
                "created_at": datetime(2025, 3, 1),
                "updated_at": datetime(2025, 3, 1),
            },
            {
                "id": "mock_005",
                "company_id": company_id,
                "filename": "leave_policy_fy2025.pdf",
                "original_filename": "leave_policy_fy2025.pdf",
                "policy_type": "leave_policy",
                "state": "all",
                "version": 1,
                "status": "processed",
                "file_size": 256000,
                "file_type": "pdf",
                "chunk_count": 10,
                "embedding_status": "completed",
                "tags": ["leave", "hr"],
                "created_at": datetime(2025, 4, 1),
                "updated_at": datetime(2025, 4, 1),
            },
        ]
        return {"policies": mock_policies, "total": len(mock_policies), "page": page, "page_size": page_size}
