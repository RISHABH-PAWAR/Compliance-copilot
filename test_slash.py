import requests

URL = "http://127.0.0.1:8000/api/v1/auth/login"
payload = {"email": "hr@demo.com", "password": "hr123"}

print("Logging in...")
res = requests.post(URL, json=payload)
if res.status_code != 200:
    print(f"Login failed: {res.status_code}")
    exit()

token = res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test List Policies WITHOUT trailing slash
print("\nTesting List Policies WITHOUT trailing slash...")
url_no_slash = "http://127.0.0.1:8000/api/v1/policies"
res_no_slash = requests.get(url_no_slash, headers=headers)
print(f"URL: {url_no_slash}")
print(f"Status: {res_no_slash.status_code}")
print(f"History: {res_no_slash.history}")
if res_no_slash.history:
    print(f"Redirected from {res_no_slash.history[0].url} to {res_no_slash.url}")
    print(f"Redirect Status: {res_no_slash.history[0].status_code}")
