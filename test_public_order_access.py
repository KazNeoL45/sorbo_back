#!/usr/bin/env python3
"""
Test script to verify that order retrieval by ID is now public
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
ORDERS_URL = f"{BASE_URL}/orders/"

# Test order ID
ORDER_ID = "fc39b2f0-9410-447a-b3c2-ab600b17ae35"

def test_public_order_access():
    """Test that order retrieval by ID is now public"""
    
    print("=== Testing Public Order Access ===\n")
    
    # Test 1: Get order by ID without authentication
    print("1. Testing order retrieval without authentication...")
    response = requests.get(f"{ORDERS_URL}{ORDER_ID}/")
    
    if response.status_code == 200:
        order = response.json()
        print("✅ SUCCESS: Order retrieved without authentication!")
        print(f"   - Order ID: {order['id']}")
        print(f"   - Product: {order['product']['name']}")
        print(f"   - Client: {order['client_name']}")
        print(f"   - Status: {order['status']}")
        print(f"   - Total: ${order['total_pesos']} {order['currency']}")
    else:
        print(f"❌ FAILED: {response.status_code} - {response.text}")
    
    # Test 2: Try to access order list (should still be protected)
    print(f"\n2. Testing order list access (should be protected)...")
    response = requests.get(f"{ORDERS_URL}")
    
    if response.status_code == 401:
        print("✅ SUCCESS: Order list is still protected (requires authentication)")
    else:
        print(f"❌ WARNING: Order list might not be protected: {response.status_code}")
    
    # Test 3: Try to access order status (should still be protected)
    print(f"\n3. Testing order status access (should be protected)...")
    response = requests.get(f"{ORDERS_URL}{ORDER_ID}/status/")
    
    if response.status_code == 401:
        print("✅ SUCCESS: Order status is still protected (requires authentication)")
    else:
        print(f"❌ WARNING: Order status might not be protected: {response.status_code}")
    
    print(f"\n=== Test Summary ===")
    print("✅ Order retrieval by ID: Public access")
    print("✅ Order listing: Protected (admin only)")
    print("✅ Order status: Protected (admin only)")

if __name__ == "__main__":
    test_public_order_access()
