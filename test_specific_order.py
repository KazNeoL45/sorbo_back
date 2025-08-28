#!/usr/bin/env python3
"""
Test script to check the status of a specific order
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
ORDERS_URL = f"{BASE_URL}/orders/"

# Test credentials
TEST_CREDENTIALS = {
    "username": "s0rb0mx24",
    "password": "s0rb0s0rb1t0"
}

# Specific order to test
ORDER_ID = "fc39b2f0-9410-447a-b3c2-ab600b17ae35"

def login():
    """Login and get access token"""
    response = requests.post(LOGIN_URL, json=TEST_CREDENTIALS)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def check_order_status(order_id, token):
    """Check order status"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/status/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order status: {response.status_code} - {response.text}")
        return None

def manual_check_stripe_status(order_id, token):
    """Manually check and update order status based on Stripe session"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{ORDERS_URL}{order_id}/check_stripe_status/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to check Stripe status: {response.status_code} - {response.text}")
        return None

def get_order_details(order_id, token):
    """Get full order details"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order details: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Testing Specific Order Status ===\n")
    
    # 1. Login to get access token
    print("1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful\n")
    
    # 2. Check current order status
    print(f"2. Checking current status for order: {ORDER_ID}")
    current_status = check_order_status(ORDER_ID, token)
    if current_status:
        print(f"✅ Current status: {current_status['status']}")
        print(f"   Created: {current_status['created_at']}")
        print(f"   Updated: {current_status['updated_at']}")
    
    # 3. Get full order details
    print(f"\n3. Getting full order details...")
    order_details = get_order_details(ORDER_ID, token)
    if order_details:
        print(f"✅ Order details:")
        print(f"   - Product: {order_details['product']['name']}")
        print(f"   - Client: {order_details['client_name']}")
        print(f"   - Email: {order_details['client_email']}")
        print(f"   - Status: {order_details['status']}")
        print(f"   - Stripe Session ID: {order_details['stripe_session_id']}")
        print(f"   - Total: ${order_details['total_pesos']} {order_details['currency']}")
    
    # 4. Test manual status check
    print(f"\n4. Testing manual Stripe status check...")
    stripe_status = manual_check_stripe_status(ORDER_ID, token)
    if stripe_status:
        print(f"✅ Manual check response:")
        print(f"   - Order ID: {stripe_status['order_id']}")
        print(f"   - Stripe Session ID: {stripe_status['stripe_session_id']}")
        print(f"   - Stripe Payment Status: {stripe_status['stripe_payment_status']}")
        print(f"   - Stripe Session Status: {stripe_status['stripe_session_status']}")
        print(f"   - Order Status: {stripe_status['order_status']}")
        print(f"   - Message: {stripe_status['message']}")
    
    # 5. Check updated order status
    print(f"\n5. Checking updated order status...")
    updated_status = check_order_status(ORDER_ID, token)
    if updated_status:
        print(f"✅ Updated status: {updated_status['status']}")
        print(f"   Updated: {updated_status['updated_at']}")
    
    print("\n=== Test Summary ===")
    if current_status and updated_status:
        if current_status['status'] != updated_status['status']:
            print(f"✅ Status changed from '{current_status['status']}' to '{updated_status['status']}'")
        else:
            print(f"ℹ️  Status remained '{current_status['status']}'")
    
    if stripe_status:
        print(f"✅ Stripe payment status: {stripe_status['stripe_payment_status']}")
        print(f"✅ Stripe session status: {stripe_status['stripe_session_status']}")

if __name__ == "__main__":
    main()
