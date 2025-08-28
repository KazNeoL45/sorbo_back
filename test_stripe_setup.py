#!/usr/bin/env python3
"""
Test script to verify Stripe configuration and test payment flow
"""

import requests
import json
import os
from datetime import datetime

def test_stripe_configuration():
    """Test if Stripe keys are properly configured"""
    print("🔧 Testing Stripe Configuration")
    print("=" * 50)
    
    # Check if keys are set
    publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'not_set')
    secret_key = os.environ.get('STRIPE_SECRET_KEY', 'not_set')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'not_set')
    
    print(f"Publishable Key: {'✅ Set' if publishable_key != 'not_set' else '❌ Not set'}")
    print(f"Secret Key: {'✅ Set' if secret_key != 'not_set' else '❌ Not set'}")
    print(f"Webhook Secret: {'✅ Set' if webhook_secret != 'not_set' else '❌ Not set'}")
    
    if 'test' in publishable_key and 'test' in secret_key:
        print("✅ Using TEST keys (safe for development)")
    elif 'live' in publishable_key and 'live' in secret_key:
        print("⚠️  Using LIVE keys (real payments will be processed)")
    else:
        print("❌ Keys not properly configured")

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Test products endpoint
    try:
        response = requests.get(f"{base_url}/api/products/")
        if response.status_code == 200:
            products = response.json()
            print(f"✅ Products endpoint: {len(products.get('results', []))} products found")
            return products.get('results', [])
        else:
            print(f"❌ Products endpoint failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Products endpoint error: {e}")
        return []

def test_authentication():
    """Test authentication and get JWT token"""
    print("\n🔐 Testing Authentication")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/api/login/"
    data = {
        "username": "s0rb0mx24",
        "password": "s0rb0s0rb1t0"
    }
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            print("✅ Authentication successful")
            return access_token
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def test_order_creation(access_token, products):
    """Test order creation with Stripe checkout"""
    if not access_token or not products:
        print("❌ Cannot test order creation - missing token or products")
        return
    
    print("\n🛒 Testing Order Creation")
    print("=" * 50)
    
    # Use the first product
    product = products[0]
    product_id = product['id']
    
    url = "http://127.0.0.1:8000/api/orders/"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "product_id": product_id,
        "buyer_full_name": "Test User",
        "buyer_address": "123 Test St, Test City, Test Country",
        "total_cents": product['price_cents'],
        "currency": product['currency']
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 201:
            order_data = response.json()
            print("✅ Order created successfully!")
            print(f"Order ID: {order_data.get('order_id')}")
            print(f"Checkout URL: {order_data.get('checkout_url')}")
            print(f"Session ID: {order_data.get('session_id')}")
            return order_data
        else:
            print(f"❌ Order creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Order creation error: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Stripe Setup Verification")
    print("=" * 60)
    print(f"Test run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test configuration
    test_stripe_configuration()
    
    # Test API endpoints
    products = test_api_endpoints()
    
    # Test authentication
    access_token = test_authentication()
    
    # Test order creation
    if access_token and products:
        test_order_creation(access_token, products)
    
    print("\n" + "=" * 60)
    print("✅ Testing completed!")
    print("\n📋 Next Steps:")
    print("1. Set up your Stripe keys in environment variables")
    print("2. Configure webhook endpoint in Stripe Dashboard")
    print("3. Test with Stripe's test card numbers")
    print("4. Check the STRIPE_SETUP.md file for detailed instructions")

if __name__ == "__main__":
    main()
