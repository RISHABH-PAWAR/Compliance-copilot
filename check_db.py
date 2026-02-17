import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

# Force SQLite path to backend dir
os.chdir(os.path.join(os.getcwd(), "backend"))

from app.core.database import SessionLocal
from app.models.sql.user import User

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Total users: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Email: {u.email}, Active: {u.is_active}, Role: {u.role}")
finally:
    db.close()
