#!/usr/bin/env python3
"""
Test script to verify that the products endpoint is publicly accessible
"""

import requests
import json

def test_products_endpoint():
    """Test the products endpoint without authentication"""
    
    # Test the products endpoint
    url = "http://127.0.0.1:8000/api/products/"
    
    try:
        print(f"Testing GET {url}")
        print("Expected: 200 OK (no authentication required)")
        print("-" * 50)
        
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Products endpoint is publicly accessible!")
            try:
                data = response.json()
                print(f"Response Data: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response Text: {response.text}")
        else:
            print("❌ FAILED: Products endpoint still requires authentication")
            print(f"Response Text: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Make sure the server is running on http://127.0.0.1:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_products_endpoint()
