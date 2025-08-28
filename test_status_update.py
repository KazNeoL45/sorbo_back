#!/usr/bin/env python3
"""
Test script for order status updates
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
ORDERS_URL = f"{BASE_URL}/api/orders/"
LOGIN_URL = f"{BASE_URL}/api/login/"

# Test credentials
USERNAME = "admin"
PASSWORD = "admin123"

def login():
    """Login and get authentication token"""
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(LOGIN_URL, json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def get_orders(token):
    """Get all orders"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(ORDERS_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get orders: {response.status_code}")
        print(response.text)
        return None

def update_order_status(token, order_id, new_status):
    """Update order status using PATCH method"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "status": new_status
    }
    
    url = f"{ORDERS_URL}{order_id}/"
    response = requests.patch(url, headers=headers, json=data)
    
    print(f"\n--- Status Update Test ---")
    print(f"Order ID: {order_id}")
    print(f"New Status: {new_status}")
    print(f"Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ Success!")
        print(f"Message: {result.get('message')}")
        print(f"Old Status: {result.get('old_status')}")
        print(f"New Status: {result.get('new_status')}")
        return result
    else:
        print("❌ Failed!")
        print(f"Error: {response.text}")
        return None

def test_status_update_endpoint(token, order_id, new_status):
    """Test the dedicated status update endpoint"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "status": new_status
    }
    
    url = f"{ORDERS_URL}{order_id}/update_status/"
    response = requests.patch(url, headers=headers, json=data)
    
    print(f"\n--- Status Update Endpoint Test ---")
    print(f"Order ID: {order_id}")
    print(f"New Status: {new_status}")
    print(f"Response Status: {response.status_code}")
    
    if response.status_code in [200, 201]:
        result = response.json()
        print("✅ Success!")
        print(f"Message: {result.get('message')}")
        print(f"Old Status: {result.get('old_status')}")
        print(f"New Status: {result.get('new_status')}")
        return result
    else:
        print("❌ Failed!")
        print(f"Error: {response.text}")
        return None

def main():
    print("🔐 Logging in...")
    token = login()
    
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful!")
    
    print("\n📋 Getting orders...")
    orders = get_orders(token)
    
    if not orders:
        print("❌ Failed to get orders. Exiting.")
        return
    
    print(f"✅ Found {len(orders.get('results', []))} orders")
    
    # Find a success order to test with
    success_orders = []
    for order in orders.get('results', []):
        if order.get('status') == 'success':
            success_orders.append(order)
    
    if not success_orders:
        print("❌ No orders with 'success' status found. Cannot test status updates.")
        return
    
    test_order = success_orders[0]
    order_id = test_order['id']
    
    print(f"\n🎯 Testing with order: {order_id}")
    print(f"Current status: {test_order['status']}")
    print(f"Client: {test_order['client_name']}")
    
    # Test 1: Update to 'sent' status
    print("\n" + "="*50)
    print("TEST 1: Update status to 'sent'")
    print("="*50)
    result1 = update_order_status(token, order_id, 'sent')
    
    if result1:
        # Test 2: Update to 'shipped' status
        print("\n" + "="*50)
        print("TEST 2: Update status to 'shipped'")
        print("="*50)
        result2 = update_order_status(token, order_id, 'shipped')
        
        if result2:
            # Test 3: Update to 'delivered' status
            print("\n" + "="*50)
            print("TEST 3: Update status to 'delivered'")
            print("="*50)
            result3 = update_order_status(token, order_id, 'delivered')
    
    # Test 4: Test invalid status transition
    print("\n" + "="*50)
    print("TEST 4: Test invalid status transition (delivered -> sent)")
    print("="*50)
    result4 = update_order_status(token, order_id, 'sent')
    
    # Test 5: Test the dedicated update_status endpoint
    print("\n" + "="*50)
    print("TEST 5: Test dedicated update_status endpoint")
    print("="*50)
    
    # Find another success order for this test
    if len(success_orders) > 1:
        test_order2 = success_orders[1]
        order_id2 = test_order2['id']
        print(f"Testing with order: {order_id2}")
        result5 = test_status_update_endpoint(token, order_id2, 'sent')
    else:
        print("Only one success order available, skipping dedicated endpoint test")
    
    print("\n" + "="*50)
    print("🎉 Testing completed!")
    print("="*50)

if __name__ == "__main__":
    main()
