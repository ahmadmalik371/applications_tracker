import urllib.request, json

# Login
data = json.dumps({'email': 'admin@techcorp.com', 'password': 'password123'}).encode()
req = urllib.request.Request('http://localhost:8000/api/v1/auth/login', data=data, headers={'Content-Type': 'application/json'})
resp = urllib.request.urlopen(req)
d = json.loads(resp.read())
token = d['access_token']
print("TOKEN_OBTAINED")

# Dashboard stats
req2 = urllib.request.Request('http://localhost:8000/api/v1/dashboard/stats', headers={'Authorization': f'Bearer {token}'})
resp2 = urllib.request.urlopen(req2)
stats = json.loads(resp2.read())
print("DASHBOARD_STATS:")
print(json.dumps(stats, indent=2))
