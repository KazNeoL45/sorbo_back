#!/usr/bin/env python3
"""
Simple script to search for a specific order by ID
"""

import requests
import json
import sys

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
ORDERS_URL = f"{BASE_URL}/orders/"

# Test credentials
TEST_CREDENTIALS = {
    "username": "s0rb0mx24",
    "password": "s0rb0s0rb1t0"
}

def login():
    """Login and get access token"""
    response = requests.post(LOGIN_URL, json=TEST_CREDENTIALS)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def search_order_by_id(order_id, token):
    """Search for a specific order by ID"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"❌ Order not found: {order_id}")
        return None
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return None

def check_order_status(order_id, token):
    """Check order status"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/status/", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error getting status: {response.status_code} - {response.text}")
        return None

def main():
    # Get order ID from command line argument or use default
    if len(sys.argv) > 1:
        order_id = sys.argv[1]
    else:
        order_id = input("Enter order ID to search: ").strip()
    
    if not order_id:
        print("❌ No order ID provided")
        return
    
    print(f"=== Searching for Order: {order_id} ===\n")
    
    # 1. Login
    print("1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful\n")
    
    # 2. Search for order
    print("2. Searching for order...")
    order = search_order_by_id(order_id, token)
    
    if order:
        print("✅ Order found!")
        print(f"   - ID: {order['id']}")
        print(f"   - Product: {order['product']['name']}")
        print(f"   - Client: {order['client_name']}")
        print(f"   - Email: {order['client_email']}")
        print(f"   - Status: {order['status']}")
        print(f"   - Total: ${order['total_pesos']} {order['currency']}")
        print(f"   - Created: {order['created_at']}")
        print(f"   - Updated: {order['updated_at']}")
        
        # 3. Check status separately
        print(f"\n3. Checking order status...")
        status = check_order_status(order_id, token)
        if status:
            print(f"✅ Status: {status['status']}")
            print(f"   Updated: {status['updated_at']}")
    
    else:
        print("❌ Order not found or error occurred")

if __name__ == "__main__":
    main()
