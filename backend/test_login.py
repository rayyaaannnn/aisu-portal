#!/usr/bin/env python3
# =============================================================
#  test_login.py — Test authentication endpoints
# =============================================================
import requests
import json
from colorama import Fore, Style

BASE_URL = "http://localhost:5000/api/auth"

def print_header(title):
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

def print_success(msg):
    print(f"{Fore.GREEN}✓ {msg}{Style.RESET_ALL}")

def print_error(msg):
    print(f"{Fore.RED}✗ {msg}{Style.RESET_ALL}")

def print_json(obj):
    print(json.dumps(obj, indent=2))

# Test 1: Create Admin User
def test_admin_seed():
    print_header("TEST 1: Admin User Pre-seeded")
    print("Default admin during startup:")
    print(f"  Email: admin@aisu4india.in")
    print(f"  Password: Admin@AISU2024")
    print(f"  Role: national")
    print_success("Should be in database automatically")

# Test 2: Register New User
def test_register():
    print_header("TEST 2: Register New User")
    payload = {
        "name": "Test User",
        "email": f"testuser@example.com",
        "mobile": "9876543210",
        "password": "TestPass123!",
        "state": "Bihar"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=payload, timeout=5)
        data = response.json()
        
        if response.status_code == 201 and data.get('success'):
            print_success(f"User registered: {payload['email']}")
            print(f"  Access Token: {data['data']['access_token'][:50]}...")
            return data['data']['access_token'], payload['email']
        else:
            print_error(f"Registration failed: {data.get('message', 'Unknown error')}")
            return None, None
    except Exception as e:
        print_error(f"Request error: {e}")
        return None, None

# Test 3: Login with Email
def test_login_email():
    print_header("TEST 3: Login with Email")
    payload = {
        "identifier": "admin@aisu4india.in",
        "password": "Admin@AISU2024"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success(f"Login successful: {data['data']['user']['name']}")
            print(f"  Role: {data['data']['user']['role']}")
            print(f"  Access Token: {data['data']['access_token'][:50]}...")
            return data['data']['access_token']
        else:
            print_error(f"Login failed: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Request error: {e}")
        return None

# Test 4: Get Current User Profile
def test_get_me(access_token):
    print_header("TEST 4: Get Current User Profile (/me)")
    
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.get(f"{BASE_URL}/me", headers=headers, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            user = data['data']
            print_success(f"Profile retrieved for: {user['name']}")
            print(f"  Email: {user['email']}")
            print(f"  Mobile: {user.get('mobile', 'N/A')}")
            print(f"  Role: {user['role']}")
            print(f"  State: {user.get('state', 'N/A')}")
            if user.get('primary_membership'):
                print(f"  Primary Membership: {user['primary_membership']['status']}")
            if user.get('student_membership'):
                print(f"  Student Membership: {user['student_membership']['status']}")
        else:
            print_error(f"Failed to get profile: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print_error(f"Request error: {e}")

# Test 5: Refresh Token
def test_refresh_token(refresh_token):
    print_header("TEST 5: Refresh Access Token")
    
    headers = {"Authorization": f"Bearer {refresh_token}"}
    try:
        response = requests.post(f"{BASE_URL}/refresh", headers=headers, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("Token refreshed successfully")
            print(f"  New Access Token: {data['data']['access_token'][:50]}...")
            return data['data']['access_token']
        else:
            print_error(f"Token refresh failed: {data.get('message', 'Unknown error')}")
            return None
    except Exception as e:
        print_error(f"Request error: {e}")
        return None

# Test 6: Forgot Password Flow
def test_forgot_password():
    print_header("TEST 6: Forgot Password - Request OTP")
    
    payload = {"identifier": "admin@aisu4india.in"}
    try:
        response = requests.post(f"{BASE_URL}/forgot-password/request", json=payload, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("OTP sent to registered email")
            print(f"  Masked Email: {data['data'].get('masked_email', 'N/A')}")
            print_success("Check email for 6-digit code (valid for 15 minutes)")
        else:
            print_error(f"Request failed: {data.get('message', 'Unknown error')}")
    except Exception as e:
        print_error(f"Request error: {e}")

# Test 7: Invalid Login
def test_invalid_login():
    print_header("TEST 7: Invalid Login (Expected to Fail)")
    
    payload = {
        "identifier": "nonexistent@example.com",
        "password": "WrongPassword123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login", json=payload, timeout=5)
        data = response.json()
        
        if response.status_code != 200:
            print_success(f"Correctly rejected: {data.get('message', 'Invalid credentials')}")
        else:
            print_error(f"Should have failed but got: {data}")
    except Exception as e:
        print_error(f"Request error: {e}")

# Test 8: Change Password
def test_change_password(access_token):
    print_header("TEST 8: Change Password")
    
    payload = {
        "old_password": "Admin@AISU2024",
        "new_password": "NewAdmin@AISU2024!"
    }
    
    headers = {"Authorization": f"Bearer {access_token}"}
    try:
        response = requests.post(f"{BASE_URL}/change-password", json=payload, headers=headers, timeout=5)
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            print_success("Password changed successfully")
            print("⚠️  Note: You'll need to login with the new password next time")
            return True
        else:
            print_error(f"Failed: {data.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print_error(f"Request error: {e}")
        return False

# Main test runner
def main():
    print(f"\n{Fore.YELLOW}AISU Authentication Tests{Style.RESET_ALL}")
    print(f"Base URL: {BASE_URL}\n")
    
    # Check server
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print_success("✓ Backend server is running on http://localhost:5000")
        else:
            print_error("Backend error")
    except:
        print_error("⚠️  Backend server is NOT running!")
        print("   Start it with: python backend/app.py")
        return

    # Run tests
    test_admin_seed()
    test_register()
    test_invalid_login()
    access_token = test_login_email()
    
    if access_token:
        test_get_me(access_token)
        
        # Test refresh (requires refresh token from login)
        payload = {
            "identifier": "admin@aisu4india.in",
            "password": "Admin@AISU2024"
        }
        try:
            response = requests.post(f"{BASE_URL}/login", json=payload)
            data = response.json()
            if data.get('data', {}).get('refresh_token'):
                new_token = test_refresh_token(data['data']['refresh_token'])
                if new_token:
                    test_get_me(new_token)
        except:
            pass
        
        test_forgot_password()
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  Tests Complete!")
    print(f"{'='*60}{Style.RESET_ALL}\n")

if __name__ == '__main__':
    main()
