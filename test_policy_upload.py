import requests

URL = "http://127.0.0.1:8000/api/v1/auth/login"
payload = {"email": "hr@demo.com", "password": "hr123"}

print("Logging in...")
res = requests.post(URL, json=payload)
if res.status_code != 200:
    print(f"Login failed: {res.status_code}")
    print(res.text)
    exit()

token = res.json()["access_token"]
print("Login successful.")

headers = {"Authorization": f"Bearer {token}"}

# Test Upload Policy
print("\nTesting Upload Policy...")
files = {"file": ("test.txt", "This is a test policy", "text/plain")}
data = {"policy_type": "hr_manual", "state": "all", "department": "HR"}

upload_res = requests.post("http://127.0.0.1:8000/api/v1/policies/upload", headers=headers, files=files, data=data)
print(f"Upload Result: {upload_res.status_code}")
print(upload_res.text)
