"""AI Compliance Copilot - FastAPI Application Entry Point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import get_settings
from app.core.database import engine, Base
from app.api.v1 import auth, companies, policies, regulations, compliance, alerts, reports, dashboard, webhooks
from app.middleware.tenant_isolation import TenantIsolationMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.middleware.audit_logger import AuditLoggerMiddleware
from app.middleware.error_handler import register_error_handlers

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Seed default data
    from app.core.database import SessionLocal
    from app.models.sql.user import User, UserRole
    from app.models.sql.company import Company
    from app.core.security import hash_password
    
    db = SessionLocal()
    try:
        # Check if company exists
        company = db.query(Company).filter(Company.id == 1).first()
        if not company:
            company = Company(id=1, name="Default Corp", industry_type="manufacturing")
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # Check if default user exists
        user = db.query(User).filter(User.email == "hr@demo.com").first()
        if not user:
            user = User(
                email="hr@demo.com",
                hashed_password=hash_password("hr123"),
                full_name="HR Admin",
                role=UserRole.HR_HEAD.value,
                company_id=1,
                is_active=True,
                is_verified=True
            )
            db.add(user)
            db.commit()
    finally:
        db.close()
    
    yield
    # Shutdown: Cleanup


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered Labor Law Compliance Engine for Indian Manufacturing & Service Companies",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Custom Middleware
app.add_middleware(TenantIsolationMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(AuditLoggerMiddleware)

# CORS Middleware - MUST BE LAST TO BE OUTERMOST
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error Handlers
register_error_handlers(app)

# API Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(companies.router, prefix=f"{settings.API_V1_PREFIX}/companies", tags=["Companies"])
app.include_router(policies.router, prefix=f"{settings.API_V1_PREFIX}/policies", tags=["Policies"])
app.include_router(regulations.router, prefix=f"{settings.API_V1_PREFIX}/regulations", tags=["Regulations"])
app.include_router(compliance.router, prefix=f"{settings.API_V1_PREFIX}/compliance", tags=["Compliance"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_PREFIX}/alerts", tags=["Alerts"])
app.include_router(reports.router, prefix=f"{settings.API_V1_PREFIX}/reports", tags=["Reports"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_PREFIX}/dashboard", tags=["Dashboard"])
app.include_router(webhooks.router, prefix=f"{settings.API_V1_PREFIX}/webhooks", tags=["Webhooks"])


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "operational",
        "environment": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
