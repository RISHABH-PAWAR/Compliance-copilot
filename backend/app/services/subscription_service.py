"""Subscription Service"""
from sqlalchemy.orm import Session
from app.models.sql.subscription import Subscription


PLAN_CONFIG = {
    "starter": {"monthly_price": 25000, "max_states": 1, "max_employees": 250, "max_users": 5,
                "has_api_access": False, "has_slack_integration": False, "has_custom_workflows": False, "has_white_label": False, "setup_fee": 15000},
    "professional": {"monthly_price": 50000, "max_states": 3, "max_employees": 500, "max_users": 15,
                     "has_api_access": False, "has_slack_integration": True, "has_custom_workflows": False, "has_white_label": False, "setup_fee": 25000},
    "enterprise": {"monthly_price": 125000, "max_states": 99, "max_employees": 1000, "max_users": 50,
                   "has_api_access": True, "has_slack_integration": True, "has_custom_workflows": True, "has_white_label": True, "setup_fee": 40000},
}


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, company_id: int, plan: str = "starter") -> Subscription:
        config = PLAN_CONFIG.get(plan, PLAN_CONFIG["starter"])
        sub = Subscription(company_id=company_id, plan=plan, **config)
        self.db.add(sub)
        self.db.commit()
        self.db.refresh(sub)
        return sub

    def get_active(self, company_id: int) -> Subscription:
        return self.db.query(Subscription).filter(
            Subscription.company_id == company_id, Subscription.status == "active"
        ).first()

    def upgrade(self, company_id: int, new_plan: str) -> Subscription:
        sub = self.get_active(company_id)
        if sub:
            config = PLAN_CONFIG.get(new_plan, PLAN_CONFIG["starter"])
            for k, v in config.items():
                setattr(sub, k, v)
            sub.plan = new_plan
            self.db.commit()
            self.db.refresh(sub)
        return sub
