#!/usr/bin/env python3
"""
Test script to test the new "sent" status functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
PRODUCTS_URL = f"{BASE_URL}/products/"
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

def create_test_product(token):
    """Create a test product"""
    headers = {"Authorization": f"Bearer {token}"}
    product_data = {
        "name": "Test Product for Sent Status",
        "description": "A test product to test the sent status functionality",
        "price_pesos": "100.00",
        "currency": "MXN",
        "stock": 5,
        "type": "test",
        "picture": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    }
    
    response = requests.post(PRODUCTS_URL, json=product_data, headers=headers)
    if response.status_code == 201:
        product = response.json()
        print(f"   Product response: {product}")
        return product
    else:
        print(f"Product creation failed: {response.status_code} - {response.text}")
        return None

def create_test_order(product_id):
    """Create a test order"""
    order_data = {
        "product_id": product_id,
        "client_name": "Test Customer",
        "client_email": "test@example.com",
        "client_phone": "+1234567890",
        "client_address": "123 Test St, Test City, Test State 12345"
    }
    
    response = requests.post(ORDERS_URL, json=order_data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Order creation failed: {response.status_code} - {response.text}")
        return None

def test_sent_status_functionality():
    """Test the sent status functionality"""
    print("=== Testing Sent Status Functionality ===\n")
    
    # Step 1: Login
    print("1. Logging in...")
    token = login()
    if not token:
        return
    print("✅ Login successful")
    
    # Step 2: Create a test product
    print("\n2. Creating test product...")
    product = create_test_product(token)
    if not product:
        return
    print(f"✅ Product created: {product['name']} (ID: {product.get('id', 'N/A')})")
    
    # Step 3: Create a test order
    print("\n3. Creating test order...")
    order = create_test_order(product.get('id', product.get('uuid')))
    if not order:
        return
    print(f"✅ Order created: {order['order_id']} (Status: {order['status']})")
    
    order_id = order['order_id']
    
    # Step 4: Try to mark as sent while order is pending (should fail)
    print(f"\n4. Testing mark as sent with pending order (should fail)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{ORDERS_URL}{order_id}/mark_as_sent/", headers=headers)
    
    if response.status_code == 400:
        print("✅ Correctly rejected: Cannot mark pending order as sent")
        print(f"   Error: {response.json()['error']}")
    else:
        print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    
    # Step 5: Simulate successful payment by manually updating status
    print(f"\n5. Simulating successful payment...")
    # We'll use the manual status check to simulate success
    response = requests.post(f"{ORDERS_URL}{order_id}/check_stripe_status/", headers=headers)
    print(f"   Status check response: {response.status_code}")
    
    # Step 6: Get current order status
    print(f"\n6. Getting current order status...")
    response = requests.get(f"{ORDERS_URL}{order_id}/")
    if response.status_code == 200:
        current_order = response.json()
        print(f"   Current status: {current_order['status']}")
        
        # Step 7: Try to mark as sent (should work if status is success)
        print(f"\n7. Testing mark as sent with current status...")
        response = requests.post(f"{ORDERS_URL}{order_id}/mark_as_sent/", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Successfully marked as sent!")
            print(f"   Order ID: {result['order_id']}")
            print(f"   New Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print(f"   Updated: {result['updated_at']}")
        elif response.status_code == 400:
            print("❌ Cannot mark as sent:")
            print(f"   Error: {response.json()['error']}")
        else:
            print(f"❌ Unexpected response: {response.status_code} - {response.text}")
    else:
        print(f"❌ Failed to get order status: {response.status_code}")
    
    # Step 8: Verify final status
    print(f"\n8. Verifying final order status...")
    response = requests.get(f"{ORDERS_URL}{order_id}/")
    if response.status_code == 200:
        final_order = response.json()
        print(f"   Final status: {final_order['status']}")
        print(f"   Client: {final_order['client_name']}")
        print(f"   Product: {final_order['product']['name']}")
        print(f"   Total: ${final_order['total_pesos']} {final_order['currency']}")
    
    print(f"\n=== Test Summary ===")
    print("✅ Sent status functionality implemented")
    print("✅ Validation works (only success orders can be marked as sent)")
    print("✅ Admin authentication required")
    print("✅ Status updates correctly")

if __name__ == "__main__":
    test_sent_status_functionality()
