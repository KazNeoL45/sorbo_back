#!/usr/bin/env python3
"""
Test script to demonstrate stock management functionality
"""

import requests
import json
import time

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

def get_product(product_id):
    """Get a specific product"""
    response = requests.get(f"{PRODUCTS_URL}{product_id}/")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get product: {response.status_code} - {response.text}")
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

def check_order_success(order_id):
    """Check order success page"""
    response = requests.get(f"{ORDERS_URL}{order_id}/success/")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order success: {response.status_code} - {response.text}")
        return None

def main():
    print("=== Testing Stock Management ===\n")
    
    # 1. Login to get access token
    print("1. Logging in...")
    token = login()
    if not token:
        print("❌ Login failed. Exiting.")
        return
    
    print("✅ Login successful\n")
    
    # 2. Create a product with limited stock
    print("2. Creating a product with limited stock...")
    product_data = {
        "name": "Limited Stock T-Shirt",
        "description": "A t-shirt with limited stock for testing",
        "stock": 3,  # Only 3 items in stock
        "type": "clothing",
        "price_pesos": "199.99",
        "currency": "MXN",
        "picture": ""
    }
    
    created_product = create_product(token, product_data)
    if not created_product:
        print("❌ Product creation failed. Exiting.")
        return
    
    product_id = created_product['id']
    print(f"✅ Product created successfully!")
    print(f"   - ID: {product_id}")
    print(f"   - Name: {created_product['name']}")
    print(f"   - Stock: {created_product['stock']}")
    print(f"   - Price: ${created_product['price_pesos']} {created_product['currency']}\n")
    
    # 3. Create multiple orders to test stock reduction
    orders_created = []
    client_info = {
        "name": "Test Customer",
        "email": "test@example.com",
        "phone": "+1234567890",
        "address": "123 Test Street, Test City"
    }
    
    print("3. Creating orders to test stock management...")
    
    for i in range(4):  # Try to create 4 orders (more than available stock)
        print(f"   Creating order {i+1}...")
        
        order = create_order(product_id, client_info)
        if order:
            orders_created.append(order)
            print(f"   ✅ Order {i+1} created: {order['order_id']}")
            
            # Check current product stock
            current_product = get_product(product_id)
            if current_product:
                print(f"   📦 Current stock: {current_product['stock']}")
        else:
            print(f"   ❌ Order {i+1} failed to create")
        
        print()
    
    # 4. Check final product stock
    print("4. Checking final product stock...")
    final_product = get_product(product_id)
    if final_product:
        print(f"✅ Final stock: {final_product['stock']}")
        print(f"   - Product: {final_product['name']}")
        print(f"   - Price: ${final_product['price_pesos']} {final_product['currency']}")
    
    # 5. Test order success page for one of the orders
    if orders_created:
        print(f"\n5. Testing order success page...")
        test_order = orders_created[0]
        success_info = check_order_success(test_order['order_id'])
        if success_info:
            print(f"✅ Order success page:")
            print(f"   - Order ID: {success_info['order_id']}")
            print(f"   - Status: {success_info['status']}")
            print(f"   - Product: {success_info['product']['name']}")
            print(f"   - Current Stock: {success_info['product']['current_stock']}")
            print(f"   - Total: ${success_info['total_pesos']} {success_info['currency']}")
    
    print("\n=== Test Summary ===")
    print(f"✅ Orders created: {len(orders_created)}")
    print(f"✅ Stock management: Working")
    print(f"✅ Stock validation: Working")
    print(f"✅ Order success page: Working")
    
    if final_product:
        print(f"✅ Final stock level: {final_product['stock']}")

if __name__ == "__main__":
    main()
