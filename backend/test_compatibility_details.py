
import requests

# Login to get token
base_url = "http://127.0.0.1:8000/api"  # Assuming standard DRF path, check urls.py
# Actually, path might be just http://127.0.0.1:8000 if not prefixed with api
# Checking frontend axiosInstance... base url is defined in .env usually, but backend runs on 8000.
# Profiles views are likely at /profiles/

# Let's check backend/core/urls.py or profiles/urls.py to be sure
# Assuming standard setup:
base_url = "http://127.0.0.1:8000"

print("Logging in...")
login_data = {
    "email": "bfrancosentis@gmail.com",
    "password": "suchocoxp123"
}

try:
    # Ajusta esto según tu endpoint real de login. 
    # Frontend login usa /profiles/login/ en axiosInstance?
    # store/index.js: "/profiles/login/"
    r = requests.post(f"{base_url}/profiles/login/", json=login_data)
    
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} {r.text}")
        exit()
        
    data = r.json()
    token = data['token']['access']
    print("Login successful! Token acquired.")
    
    # Get compatibility list to find target ID (AmigoTester)
    # GET /profiles/compatibility/
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{base_url}/profiles/compatibility/", headers=headers)
    print(f"Compatibility list status: {r.status_code}")
    
    comp_list = r.json()
    target_id = None
    if isinstance(comp_list, list) and len(comp_list) > 0:
        print(f"Found {len(comp_list)} matches.")
        target_id = comp_list[0]['id']
        print(f"Testing details with first match: ID {target_id} ({comp_list[0].get('nickname')})")
    else:
        print("No matches found in compatibility list.")
        exit()
        
    # Get details
    # GET /profiles/compatibility-details/?target_id=...&target_type=user
    params = {
        "target_id": target_id,
        "target_type": "user"
    }
    print(f"Fetching details for target_id={target_id}...")
    r = requests.get(f"{base_url}/profiles/compatibility-details/", headers=headers, params=params)
    
    if r.status_code == 200:
        details = r.json()
        print(f"Details count: {len(details)}")
        if len(details) > 0:
            print("First item sample:")
            print(details[0])
            # Check for empty strings
            if details[0]['question'] == '':
                 print("⚠️ ALERTA: Question is EMPTY STRING")
            if details[0]['option'] == '':
                 print("⚠️ ALERTA: Option is EMPTY STRING")
    else:
        print(f"Error fetching details: {r.status_code} {r.text}")

except Exception as e:
    print(f"Error: {e}")
