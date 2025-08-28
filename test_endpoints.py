#!/usr/bin/env python3
"""
Test script to verify both public and authenticated endpoints
"""

import requests
import json

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    print("🔓 Testing Public Endpoints (No Auth Required)")
    print("=" * 50)
    
    # Test products endpoint
    url = "http://127.0.0.1:8000/api/products/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"✅ GET {url} - SUCCESS (200 OK)")
        else:
            print(f"❌ GET {url} - FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ GET {url} - ERROR: {e}")

def test_authentication():
    """Test authentication and get a fresh token"""
    print("\n🔐 Testing Authentication")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/api/login/"
    data = {
        "username": "s0rb0mx24",
        "password": "s0rb0s0rb1t0"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print(f"✅ Login successful - Got access token")
            return access_token
        else:
            print(f"❌ Login failed - {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_authenticated_endpoints(access_token):
    """Test endpoints that require authentication"""
    if not access_token:
        print("❌ Cannot test authenticated endpoints without token")
        return
    
    print(f"\n🔒 Testing Authenticated Endpoints")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Test orders endpoint
    url = "http://127.0.0.1:8000/api/orders/"
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✅ GET {url} - SUCCESS (200 OK)")
        else:
            print(f"❌ GET {url} - FAILED ({response.status_code}): {response.text}")
    except Exception as e:
        print(f"❌ GET {url} - ERROR: {e}")

def main():
    print("🚀 Testing SorboBackend API Endpoints")
    print("=" * 60)
    
    # Test public endpoints
    test_public_endpoints()
    
    # Test authentication
    access_token = test_authentication()
    
    # Test authenticated endpoints
    test_authenticated_endpoints(access_token)
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")

if __name__ == "__main__":
    main()
