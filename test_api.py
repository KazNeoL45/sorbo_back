#!/usr/bin/env python3
"""
Test script for SorboBackend API endpoints
Run this script to test the API functionality
"""

import requests
import json
import base64
from io import BytesIO
from PIL import Image

# API base URL
BASE_URL = "http://localhost:8000/api"

def create_test_image():
    """Create a simple test image and convert to base64"""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def test_login():
    """Test the login endpoint"""
    print("Testing login endpoint...")
    
    login_data = {
        "username": "s0rb0mx24",
        "password": "s0rb0s0rb1t0"
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Login successful!")
        print(f"Access token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_products_public(token=None):
    """Test public product endpoints"""
    print("\nTesting public product endpoints...")
    
    # Test GET /api/products/ (public)
    response = requests.get(f"{BASE_URL}/products/")
    if response.status_code == 200:
        print("✓ Product list endpoint working (public)")
        products = response.json()
        print(f"Found {products.get('count', 0)} products")
    else:
        print(f"✗ Product list failed: {response.status_code}")
        print(response.text)

def test_products_admin(token):
    """Test admin product endpoints"""
    print("\nTesting admin product endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test POST /api/products/ (admin only)
    test_image = create_test_image()
    product_data = {
        "picture": test_image,
        "name": "Test Product",
        "description": "This is a test product created by the test script",
        "stock": 10,
        "type": "test",
        "price_cents": 1999,
        "currency": "USD"
    }
    
    response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
    
    if response.status_code == 201:
        print("✓ Product creation successful!")
        product = response.json()
        product_id = product['id']
        print(f"Created product with ID: {product_id}")
        
        # Test GET /api/products/{id}/ (public)
        response = requests.get(f"{BASE_URL}/products/{product_id}/")
        if response.status_code == 200:
            print("✓ Product retrieval successful!")
        else:
            print(f"✗ Product retrieval failed: {response.status_code}")
        
        # Test PUT /api/products/{id}/ (admin only)
        update_data = {
            "name": "Updated Test Product",
            "description": "This product has been updated",
            "stock": 15,
            "type": "test",
            "price_cents": 2499,
            "currency": "USD"
        }
        
        response = requests.put(f"{BASE_URL}/products/{product_id}/", json=update_data, headers=headers)
        if response.status_code == 200:
            print("✓ Product update successful!")
        else:
            print(f"✗ Product update failed: {response.status_code}")
        
        return product_id
    else:
        print(f"✗ Product creation failed: {response.status_code}")
        print(response.text)
        return None

def test_orders(token, product_id):
    """Test order endpoints"""
    print("\nTesting order endpoints...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test POST /api/orders/ (authenticated)
    order_data = {
        "product_id": product_id,
        "buyer_full_name": "Test User",
        "buyer_address": "123 Test Street, Test City, Test Country",
        "total_cents": 2499,
        "currency": "USD"
    }
    
    response = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
    
    if response.status_code == 201:
        print("✓ Order creation successful!")
        order = response.json()
        order_id = order['order_id']
        print(f"Created order with ID: {order_id}")
        print(f"Checkout URL: {order['checkout_url']}")
        
        # Test GET /api/orders/{id}/status/ (authenticated)
        response = requests.get(f"{BASE_URL}/orders/{order_id}/status/", headers=headers)
        if response.status_code == 200:
            print("✓ Order status retrieval successful!")
            status_data = response.json()
            print(f"Order status: {status_data['status']}")
        else:
            print(f"✗ Order status retrieval failed: {response.status_code}")
        
        return order_id
    else:
        print(f"✗ Order creation failed: {response.status_code}")
        print(response.text)
        return None

def test_public_endpoints():
    """Test endpoints that don't require authentication"""
    print("\nTesting public endpoints...")
    
    # Test order success page
    response = requests.get(f"{BASE_URL}/orders/success/")
    if response.status_code == 200:
        print("✓ Order success page working")
    else:
        print(f"✗ Order success page failed: {response.status_code}")
    
    # Test order cancel page
    response = requests.get(f"{BASE_URL}/orders/cancel/")
    if response.status_code == 200:
        print("✓ Order cancel page working")
    else:
        print(f"✗ Order cancel page failed: {response.status_code}")

def main():
    """Run all tests"""
    print("🧪 SorboBackend API Test Suite")
    print("=" * 40)
    
    # Test login
    token = test_login()
    if not token:
        print("Cannot proceed without authentication token")
        return
    
    # Test public endpoints
    test_products_public(token)
    test_public_endpoints()
    
    # Test admin endpoints
    product_id = test_products_admin(token)
    if product_id:
        # Test order endpoints
        test_orders(token, product_id)
    
    print("\n" + "=" * 40)
    print("✅ Test suite completed!")
    print("\nNote: Stripe integration requires valid API keys to be configured.")
    print("Update the settings.py file with your Stripe credentials for full functionality.")

if __name__ == "__main__":
    main()
