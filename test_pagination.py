#!/usr/bin/env python3
"""
Test script to demonstrate pagination functionality
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
ORDERS_URL = f"{BASE_URL}/orders/"

# Test credentials (update these based on your settings)
TEST_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

def login():
    """Login and get access token"""
    response = requests.post(LOGIN_URL, json=TEST_CREDENTIALS)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def get_orders_with_pagination(token, page=1, page_size=25):
    """Get orders with pagination"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page, "page_size": page_size}
    
    response = requests.get(ORDERS_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get orders: {response.status_code} - {response.text}")
        return None

def test_pagination():
    """Test pagination functionality"""
    print("=== Testing Order Pagination ===\n")
    
    # 1. Login
    print("1. Logging in...")
    token = login()
    if not token:
        print("Login failed. Please check your credentials.")
        return
    print("✓ Login successful\n")
    
    # 2. Test different page sizes
    print("2. Testing different page sizes...")
    
    page_sizes = [10, 25, 50, 100]
    
    for size in page_sizes:
        print(f"\n--- Testing page size: {size} ---")
        result = get_orders_with_pagination(token, page=1, page_size=size)
        
        if result:
            print(f"✓ Total orders: {result['count']}")
            print(f"✓ Orders on this page: {len(result['results'])}")
            print(f"✓ Has next page: {'Yes' if result['next'] else 'No'}")
            print(f"✓ Has previous page: {'Yes' if result['previous'] else 'No'}")
            
            if result['results']:
                print(f"✓ First order: {result['results'][0]['client_name']} - {result['results'][0]['status']}")
                print(f"✓ Last order: {result['results'][-1]['client_name']} - {result['results'][-1]['status']}")
        else:
            print("✗ Failed to get orders")
    
    # 3. Test pagination navigation
    print("\n3. Testing pagination navigation...")
    
    # Get first page
    print("\n--- First Page (10 orders) ---")
    first_page = get_orders_with_pagination(token, page=1, page_size=10)
    
    if first_page and first_page['next']:
        print("✓ First page retrieved successfully")
        
        # Get second page
        print("\n--- Second Page (10 orders) ---")
        second_page = get_orders_with_pagination(token, page=2, page_size=10)
        
        if second_page:
            print("✓ Second page retrieved successfully")
            print(f"✓ Orders on second page: {len(second_page['results'])}")
            print(f"✓ Has previous page: {'Yes' if second_page['previous'] else 'No'}")
            
            if first_page['results'] and second_page['results']:
                print(f"✓ First page first order: {first_page['results'][0]['id']}")
                print(f"✓ Second page first order: {second_page['results'][0]['id']}")
                print(f"✓ Orders are different: {first_page['results'][0]['id'] != second_page['results'][0]['id']}")
    
    # 4. Test maximum page size
    print("\n4. Testing maximum page size...")
    
    # Try to get more than 100 orders
    large_page = get_orders_with_pagination(token, page=1, page_size=150)
    
    if large_page:
        print(f"✓ Page size 150 returned: {len(large_page['results'])} orders")
        print("Note: Should be limited to 100 orders maximum")
    else:
        print("✗ Failed to get large page")
    
    print("\n=== Pagination Testing Completed ===")
    print("\nSummary:")
    print("- Default page size: 50 orders")
    print("- Maximum page size: 100 orders")
    print("- Total orders: Unlimited (depends on database)")
    print("- Use ?page=X&page_size=Y to control pagination")

if __name__ == "__main__":
    test_pagination()
