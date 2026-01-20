import requests

# Test API endpoints
BASE_URL = "http://127.0.0.1:5000"

print("Testing Climate Pulse API Endpoints")
print("=" * 50)

# Test data-source endpoint
try:
    resp = requests.get(f"{BASE_URL}/api/data-source")
    print(f"\n1. GET /api/data-source")
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test required-columns endpoint
try:
    resp = requests.get(f"{BASE_URL}/api/required-columns")
    print(f"\n2. GET /api/required-columns")
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test locations endpoint
try:
    resp = requests.get(f"{BASE_URL}/api/locations")
    print(f"\n3. GET /api/locations")
    print(f"   Status: {resp.status_code}")
    print(f"   Locations count: {len(resp.json())}")
    print(f"   First 5 locations: {resp.json()[:5]}")
except Exception as e:
    print(f"   Error: {e}")

# Test file upload
try:
    print(f"\n4. POST /api/upload (with sample_test_data.csv)")
    with open('sample_test_data.csv', 'rb') as f:
        files = {'file': ('sample_test_data.csv', f, 'text/csv')}
        resp = requests.post(f"{BASE_URL}/api/upload", files=files)
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test locations after upload (should show new locations in same session)
try:
    session = requests.Session()
    with open('sample_test_data.csv', 'rb') as f:
        files = {'file': ('sample_test_data.csv', f, 'text/csv')}
        resp = session.post(f"{BASE_URL}/api/upload", files=files)
    
    print(f"\n5. GET /api/locations (after upload in same session)")
    resp = session.get(f"{BASE_URL}/api/locations")
    print(f"   Status: {resp.status_code}")
    print(f"   Locations: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

# Test reset
try:
    session = requests.Session()
    # First upload
    with open('sample_test_data.csv', 'rb') as f:
        files = {'file': ('sample_test_data.csv', f, 'text/csv')}
        session.post(f"{BASE_URL}/api/upload", files=files)
    
    # Check data source
    resp = session.get(f"{BASE_URL}/api/data-source")
    print(f"\n6. Data source after upload: {resp.json()}")
    
    # Reset
    resp = session.post(f"{BASE_URL}/api/reset-data")
    print(f"\n7. POST /api/reset-data")
    print(f"   Status: {resp.status_code}")
    print(f"   Response: {resp.json()}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 50)
print("API Tests Complete!")
