"""Database Seed Script"""
import sys
sys.path.insert(0, ".")

from app.core.database import SessionLocal, engine, Base
from app.models.sql import User, Company, Regulation, RegulationRule, Subscription
from app.core.security import hash_password
from datetime import datetime, date


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Company
    company = db.query(Company).filter(Company.name == "Demo Manufacturing Pvt Ltd").first()
    if not company:
        company = Company(
            name="Demo Manufacturing Pvt Ltd", industry_type="manufacturing",
            employee_count=450, operational_states=["MH", "GJ", "KA"],
            gstin="27AAACR5055K1Z5", pan="AAACR5055K",
            subscription_plan="professional",
        )
        db.add(company)
        db.commit()
        db.refresh(company)

    # Admin user
    if not db.query(User).filter(User.email == "admin@demo.com").first():
        db.add(User(email="admin@demo.com", full_name="Admin User",
                     hashed_password=hash_password("admin123"), role="admin",
                     company_id=company.id, is_active=True))

    # HR user
    if not db.query(User).filter(User.email == "hr@demo.com").first():
        db.add(User(email="hr@demo.com", full_name="HR Manager",
                     hashed_password=hash_password("hr123"), role="hr_admin",
                     company_id=company.id, is_active=True))

    # Regulations & rules
    regs_data = [
        ("Factories Act, 1948", "FACTORIES_ACT", "safety", "Regulates working conditions in factories", "all", "manufacturing", 10, [
            ("Sec 51", "Weekly Working Hours", "Max 48 hours per week for factory workers", "mandatory", 500000, "high"),
            ("Sec 54", "Daily Working Hours", "Max 9 hours per day", "mandatory", 200000, "high"),
            ("Sec 59", "Overtime Wages", "Overtime must be paid at double the ordinary rate", "mandatory", 500000, "critical"),
            ("Sec 52", "Weekly Holiday", "One day of rest every seven days", "mandatory", 100000, "medium"),
        ]),
        ("Minimum Wages Act, 1948", "MIN_WAGES_ACT", "wages", "Ensures minimum wages for workers", "all", "all", 1, [
            ("Sec 3", "State Minimum Wage", "Pay at least the minimum wage fixed by state government", "mandatory", 500000, "critical"),
            ("Sec 12", "Wage Payment Mode", "Wages must be paid in legal tender or through bank", "mandatory", 100000, "medium"),
            ("Sec 22", "Record Keeping", "Maintain registers of wages", "mandatory", 200000, "medium"),
        ]),
        ("Shops and Establishments Act", "SHOPS_EST_ACT", "working_conditions", "Regulates shops & commercial establishments", "state", "service", 1, [
            ("Sec 7", "Shop Registration", "Every shop must be registered with local authority", "mandatory", 50000, "high"),
            ("Sec 10", "Shop Working Hours", "Max 9 hours per day, 48 hours per week", "mandatory", 100000, "medium"),
            ("Sec 14", "Annual Leave", "Employees entitled to earned leave on completion of 12 months", "mandatory", 50000, "medium"),
        ]),
        ("EPF Act, 1952", "EPF_ACT", "social_security", "Employees Provident Fund scheme", "all", "all", 20, [
            ("Sec 6", "PF Contribution Rate", "Employer must contribute 12% of basic wages to PF", "mandatory", 1000000, "critical"),
            ("Sec 7A", "PF Calculation", "PF calculated on basic + DA + retaining allowance", "mandatory", 500000, "high"),
            ("Sec 14B", "PF Delay Penalty", "Penalty for delayed PF contributions", "penalty", 200000, "high"),
        ]),
        ("ESI Act, 1948", "ESI_ACT", "social_security", "Employees State Insurance scheme", "all", "all", 10, [
            ("Sec 38", "ESI Registration", "All eligible establishments must register with ESIC", "mandatory", 500000, "critical"),
            ("Sec 39", "ESI Contribution", "Employer 3.25% + Employee 0.75% of gross wages", "mandatory", 500000, "critical"),
            ("Sec 44", "ESI Wage Ceiling", "Applicable to employees earning up to ₹21,000/month", "threshold", 200000, "medium"),
        ]),
        ("Payment of Wages Act, 1936", "PAYMENT_WAGES_ACT", "wages", "Timely payment of wages", "all", "all", 1, [
            ("Sec 3", "Wage Payment Timeline", "Wages must be paid before 7th/10th of month", "mandatory", 200000, "high"),
            ("Sec 7", "Authorized Deductions", "Only authorized deductions can be made from wages", "mandatory", 300000, "high"),
            ("Sec 5", "No Unauthorized Deduction", "Fines and deductions cannot exceed 50% of wages", "threshold", 200000, "medium"),
        ]),
        ("Payment of Bonus Act, 1965", "BONUS_ACT", "wages", "Annual bonus for eligible employees", "all", "all", 20, [
            ("Sec 10", "Minimum Bonus", "Minimum bonus of 8.33% of salary or ₹100", "mandatory", 250000, "high"),
            ("Sec 11", "Maximum Bonus", "Maximum bonus of 20% from allocable surplus", "caps", 250000, "medium"),
            ("Sec 19", "Bonus Distribution", "Bonus must be paid within 8 months of accounting year", "deadline", 200000, "high"),
        ]),
    ]

    for act_name, code, cat, desc, states, industries, threshold, rules in regs_data:
        reg = db.query(Regulation).filter(Regulation.act_code == code).first()
        if not reg:
            reg = Regulation(act_name=act_name, act_code=code, category=cat, description=desc,
                            applicable_states=states, applicable_industries=industries,
                            min_employee_threshold=threshold)
            db.add(reg)
            db.commit()
            db.refresh(reg)

            for sec, title, requirement, req_type, penalty, severity in rules:
                db.add(RegulationRule(
                    regulation_id=reg.id, section_number=sec, rule_title=title,
                    rule_description=f"{title}: {requirement}", requirement=requirement,
                    applicable_state="all", penalty_amount=penalty, severity=severity,
                    effective_date=date(2024, 1, 1), version=1,
                ))
            db.commit()

    # Subscription
    if not db.query(Subscription).filter(Subscription.company_id == company.id).first():
        db.add(Subscription(
            company_id=company.id, plan="professional", status="active",
            monthly_price=50000, max_states=3, max_employees=500, max_users=15,
            has_api_access=False, has_slack_integration=True,
        ))
        db.commit()

    db.close()
    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()
