#!/usr/bin/env python3
"""
Test script for the new order system functionality
"""

import requests
import json
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
PRODUCTS_URL = f"{BASE_URL}/products/"
ORDERS_URL = f"{BASE_URL}/orders/"

# Test credentials (update these based on your settings)
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

def get_products():
    """Get all products"""
    response = requests.get(PRODUCTS_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get products: {response.status_code}")
        return []

def create_order(product_id, client_info):
    """Create a new order with client information"""
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

def get_all_orders(token):
    """Get all orders (requires authentication)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(ORDERS_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get orders: {response.status_code} - {response.text}")
        return []

def get_order_by_id(order_id, token):
    """Get order by ID (requires authentication)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order {order_id}: {response.status_code} - {response.text}")
        return None

def get_order_status(order_id, token):
    """Get order status (requires authentication)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/status/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order status: {response.status_code} - {response.text}")
        return None

def check_stripe_status(order_id, token):
    """Manually check and update order status based on Stripe session (requires authentication)"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{ORDERS_URL}{order_id}/check_stripe_status/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to check Stripe status: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Testing New Order System ===\n")
    
    # 1. Login to get access token
    print("1. Logging in...")
    token = login()
    if not token:
        print("Login failed. Please check your credentials.")
        return
    print("✓ Login successful\n")
    
    # 2. Get available products
    print("2. Getting available products...")
    products = get_products()
    if not products:
        print("No products available. Please create some products first.")
        return
    
    # Handle paginated response
    if isinstance(products, dict) and 'results' in products:
        products_list = products['results']
        print(f"✓ Found {products['count']} products (showing {len(products_list)}):")
    else:
        products_list = products
        print(f"✓ Found {len(products_list)} products:")
    
    for product in products_list:
        print(f"  - {product['name']} (ID: {product['id']}) - ${product['price_pesos']} {product['currency']}")
    print()
    
    # 3. Create a test order
    print("3. Creating a test order...")
    product = products_list[0]  # Use the first product
    
    client_info = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, State 12345"
    }
    
    order_result = create_order(product['id'], client_info)
    if order_result:
        order_id = order_result['order_id']
        print(f"✓ Order created successfully!")
        print(f"  Order ID: {order_id}")
        print(f"  Status: {order_result['status']}")
        print(f"  Checkout URL: {order_result['checkout_url']}")
        print()
        
        # 4. Get order by ID
        print("4. Getting order by ID...")
        order_details = get_order_by_id(order_id, token)
        if order_details:
            print("✓ Order details retrieved:")
            print(f"  Client: {order_details['client_name']}")
            print(f"  Email: {order_details['client_email']}")
            print(f"  Phone: {order_details['client_phone']}")
            print(f"  Address: {order_details['client_address']}")
            print(f"  Product: {order_details['product']['name']}")
            print(f"  Total: ${order_details['total_pesos']} {order_details['currency']}")
            print(f"  Status: {order_details['status']}")
            print()
        
        # 5. Get order status
        print("5. Getting order status...")
        status_info = get_order_status(order_id, token)
        if status_info:
            print("✓ Order status retrieved:")
            print(f"  Status: {status_info['status']}")
            print(f"  Created: {status_info['created_at']}")
            print(f"  Updated: {status_info['updated_at']}")
            print()
        
        # 6. Check Stripe status manually
        print("6. Checking Stripe status manually...")
        stripe_status = check_stripe_status(order_id, token)
        if stripe_status:
            print("✓ Stripe status check completed:")
            print(f"  Stripe Payment Status: {stripe_status['stripe_payment_status']}")
            print(f"  Stripe Session Status: {stripe_status['stripe_session_status']}")
            print(f"  Order Status: {stripe_status['order_status']}")
            print(f"  Message: {stripe_status['message']}")
            print()
    
    # 7. Get all orders
    print("7. Getting all orders...")
    all_orders = get_all_orders(token)
    if all_orders:
        print(f"✓ Found {len(all_orders)} orders:")
        for order in all_orders:
            print(f"  - Order {order['id']}: {order['client_name']} - {order['status']}")
        print()
    
    print("=== Test completed ===")
    print("\nNote: Orders start with 'pending' status and change to 'success' or 'failed'")
    print("based on the payment outcome through Stripe webhooks.")
    print("You can manually check Stripe status using the check_stripe_status endpoint.")

if __name__ == "__main__":
    main()
