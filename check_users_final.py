import sqlite3
import os

db_path = os.path.join("backend", "compliance_copilot.db")
if not os.path.exists(db_path):
    # Try current directory if backend folder isn't where we expect
    db_path = "compliance_copilot.db"

print(f"Checking database: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, is_active, is_verified FROM users")
    users = cursor.fetchall()
    print("\nUsers found:")
    for user in users:
        print(f"ID: {user[0]}, Email: {user[1]}, Role: {user[2]}, Active: {user[3]}, Verified: {user[4]}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
