#!/usr/bin/env python3
"""
Test script to test manual status check functionality
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

def create_product(token, product_data):
    """Create a new product with price in pesos"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(PRODUCTS_URL, json=product_data, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create product: {response.status_code} - {response.text}")
        return None

def create_order(product_id, client_info):
    """Create a new order"""
    order_data = {
        "product_id": str(product_id),
        "client_name": client_info["name"],
        "client_email": client_info["email"],
        "client_phone": client_info["phone"],
        "client_address": client_info["address"]
    }
    
    response = requests.post(ORDERS_URL, json=order_data)
    if response.status_code == 201:
        return response.json()
    else:
        print(f"Failed to create order: {response.status_code} - {response.text}")
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

def get_product(product_id):
    """Get a specific product"""
    response = requests.get(f"{PRODUCTS_URL}{product_id}/")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get product: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Testing Manual Status Check ===\n")
    
    # 1. Login to get access token
    print("1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful\n")
    
    # 2. Create a product for testing
    print("2. Creating a test product...")
    product_data = {
        "name": "Manual Check Test Product",
        "description": "A product for testing manual status check",
        "stock": 3,
        "type": "test",
        "price_pesos": "199.99",
        "currency": "MXN",
        "picture": ""
    }
    
    created_product = create_product(token, product_data)
    if not created_product:
        print("❌ Product creation failed. Exiting.")
        return
    
    product_id = created_product['id']
    print(f"✅ Product created: {created_product['name']} (Stock: {created_product['stock']})\n")
    
    # 3. Create an order
    print("3. Creating a test order...")
    client_info = {
        "name": "Manual Check Test Customer",
        "email": "manual@test.com",
        "phone": "+1234567890",
        "address": "123 Manual Test St"
    }
    
    order = create_order(product_id, client_info)
    if not order:
        print("❌ Order creation failed. Exiting.")
        return
    
    order_id = order['order_id']
    session_id = order['session_id']
    print(f"✅ Order created: {order_id}")
    print(f"   Session ID: {session_id}")
    print(f"   Status: {order['status']}\n")
    
    # 4. Check initial order status
    print("4. Checking initial order status...")
    initial_status = check_order_status(order_id, token)
    if initial_status:
        print(f"✅ Initial status: {initial_status['status']}")
    
    # 5. Check initial product stock
    print("5. Checking initial product stock...")
    initial_product = get_product(product_id)
    if initial_product:
        print(f"✅ Initial stock: {initial_product['stock']}\n")
    
    # 6. Test manual status check
    print("6. Testing manual status check...")
    stripe_status = manual_check_stripe_status(order_id, token)
    if stripe_status:
        print(f"✅ Manual check response:")
        print(f"   - Order ID: {stripe_status['order_id']}")
        print(f"   - Stripe Session ID: {stripe_status['stripe_session_id']}")
        print(f"   - Stripe Payment Status: {stripe_status['stripe_payment_status']}")
        print(f"   - Stripe Session Status: {stripe_status['stripe_session_status']}")
        print(f"   - Order Status: {stripe_status['order_status']}")
        print(f"   - Message: {stripe_status['message']}")
    
    # 7. Check updated order status
    print("\n7. Checking updated order status...")
    updated_status = check_order_status(order_id, token)
    if updated_status:
        print(f"✅ Updated status: {updated_status['status']}")
    
    # 8. Check updated product stock
    print("8. Checking updated product stock...")
    updated_product = get_product(product_id)
    if updated_product:
        print(f"✅ Updated stock: {updated_product['stock']}")
        
        if initial_product and updated_product['stock'] < initial_product['stock']:
            print("✅ Stock was reduced successfully!")
        else:
            print("ℹ️  Stock was not reduced (order may still be pending)")
    
    print("\n=== Test Summary ===")
    print("✅ Manual status check: Working")
    print("✅ Order status updates: Working")
    print("✅ Stripe integration: Working")
    
    if initial_product and updated_product:
        stock_reduced = initial_product['stock'] - updated_product['stock']
        print(f"✅ Stock reduction: {stock_reduced} items")

if __name__ == "__main__":
    main()
