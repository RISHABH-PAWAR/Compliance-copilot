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

# Test List Policies
print("\nTesting List Policies...")
list_res = requests.get("http://127.0.0.1:8000/api/v1/policies/", headers=headers)
print(f"List Result: {list_res.status_code}")
print(list_res.text)
