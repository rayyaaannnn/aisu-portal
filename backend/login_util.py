#!/usr/bin/env python3
# =============================================================
#  login_util.py — Simple login helper for direct use
# =============================================================
"""
Quick login utility for AISU backend.

Usage:
    from login_util import login, verify_token

    # Login
    result = login("admin@aisu4india.in", "Admin@AISU2024")
    if result['success']:
        access_token = result['access_token']
        user = result['user']
    
    # Get user profile with token
    user_profile = verify_token(access_token)
"""

import requests
import json
from typing import Dict, Optional

BASE_URL = "http://localhost:5000/api/auth"


def login(identifier: str, password: str) -> Dict:
    """
    Login to AISU backend.
    
    Args:
        identifier: Email, mobile, or member_id
        password: User password
    
    Returns:
        {
            'success': bool,
            'message': str,
            'access_token': str,
            'refresh_token': str,
            'user': {
                'id': str,
                'name': str,
                'email': str,
                'role': str,
                'state': str
            }
        }
    """
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"identifier": identifier, "password": password},
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            return {
                'success': True,
                'message': data.get('message', 'Login successful'),
                'access_token': data['data'].get('access_token'),
                'refresh_token': data['data'].get('refresh_token'),
                'user': data['data'].get('user', {})
            }
        else:
            return {
                'success': False,
                'message': data.get('message', 'Login failed'),
                'access_token': None,
                'refresh_token': None,
                'user': {}
            }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'message': 'Cannot connect to backend. Is it running?',
            'access_token': None,
            'refresh_token': None,
            'user': {}
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'access_token': None,
            'refresh_token': None,
            'user': {}
        }


def verify_token(access_token: str) -> Optional[Dict]:
    """
    Get current user profile using access token.
    
    Args:
        access_token: JWT access token from login
    
    Returns:
        User profile dict or None if invalid
    """
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(
            f"{BASE_URL}/me",
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            return data.get('data', {})
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")
        return None


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Get a new access token using refresh token.
    
    Args:
        refresh_token: JWT refresh token from login
    
    Returns:
        New access token or None
    """
    try:
        headers = {"Authorization": f"Bearer {refresh_token}"}
        response = requests.post(
            f"{BASE_URL}/refresh",
            headers=headers,
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            return data['data'].get('access_token')
        return None
    except Exception as e:
        print(f"Error refreshing token: {e}")
        return None


def register(name: str, email: str, mobile: str, password: str, state: str = "") -> Dict:
    """
    Register a new user.
    
    Args:
        name: Full name
        email: Email address
        mobile: 10-digit mobile number
        password: Password (min 6 chars)
        state: State name (optional)
    
    Returns:
        Same as login() response
    """
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={
                "name": name,
                "email": email,
                "mobile": mobile,
                "password": password,
                "state": state
            },
            timeout=10
        )
        data = response.json()
        
        if response.status_code == 201 and data.get('success'):
            return {
                'success': True,
                'message': data.get('message', 'Registration successful'),
                'access_token': data['data'].get('access_token'),
                'refresh_token': data['data'].get('refresh_token'),
                'user': data['data'].get('user', {})
            }
        else:
            return {
                'success': False,
                'message': data.get('message', 'Registration failed'),
                'access_token': None,
                'refresh_token': None,
                'user': {}
            }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'access_token': None,
            'refresh_token': None,
            'user': {}
        }


def change_password(access_token: str, old_password: str, new_password: str) -> Dict:
    """
    Change password for logged-in user.
    
    Args:
        access_token: JWT access token
        old_password: Current password
        new_password: New password (min 8 chars)
    
    Returns:
        {'success': bool, 'message': str}
    """
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(
            f"{BASE_URL}/change-password",
            json={
                "old_password": old_password,
                "new_password": new_password
            },
            headers=headers,
            timeout=10
        )
        data = response.json()
        return {
            'success': data.get('success', False),
            'message': data.get('message', 'Request failed')
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


def forgot_password_request(identifier: str) -> Dict:
    """
    Request password reset OTP.
    
    Args:
        identifier: Email or mobile
    
    Returns:
        {'success': bool, 'message': str, 'masked_email': str}
    """
    try:
        response = requests.post(
            f"{BASE_URL}/forgot-password/request",
            json={"identifier": identifier},
            timeout=10
        )
        data = response.json()
        return {
            'success': data.get('success', False),
            'message': data.get('message', 'Request failed'),
            'masked_email': data['data'].get('masked_email', '') if data.get('data') else ''
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}',
            'masked_email': ''
        }


def forgot_password_reset(identifier: str, otp: str, new_password: str) -> Dict:
    """
    Reset password using OTP.
    
    Args:
        identifier: Email or mobile
        otp: 6-digit OTP from email
        new_password: New password (min 8 chars)
    
    Returns:
        {'success': bool, 'message': str}
    """
    try:
        response = requests.post(
            f"{BASE_URL}/forgot-password/reset",
            json={
                "identifier": identifier,
                "otp": otp,
                "new_password": new_password
            },
            timeout=10
        )
        data = response.json()
        return {
            'success': data.get('success', False),
            'message': data.get('message', 'Request failed')
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error: {str(e)}'
        }


# ── Example Usage ──────────────────────────────────────────

if __name__ == '__main__':
    print("AISU Login Utility Examples\n")
    
    # Example 1: Login
    print("1. Login as admin:")
    result = login("admin@aisu4india.in", "Admin@AISU2024")
    if result['success']:
        print(f"   ✓ Logged in as {result['user']['name']}")
        print(f"   Token: {result['access_token'][:30]}...")
        
        # Example 2: Get profile
        print("\n2. Get user profile:")
        profile = verify_token(result['access_token'])
        if profile:
            print(f"   ✓ Name: {profile['name']}")
            print(f"   ✓ Email: {profile['email']}")
            print(f"   ✓ Role: {profile['role']}")
    else:
        print(f"   ✗ {result['message']}")
