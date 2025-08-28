#!/usr/bin/env python3
"""
Test script for production Stripe setup
"""

import requests
import json
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000"  # Change to your production URL
ORDERS_URL = f"{BASE_URL}/api/orders/"
PRODUCTS_URL = f"{BASE_URL}/api/products/"

def test_stripe_configuration():
    """Test if Stripe is properly configured"""
    print("🔧 Testing Stripe Configuration...")
    
    try:
        # Test if we can get products (this will use Stripe keys)
        response = requests.get(PRODUCTS_URL)
        
        if response.status_code == 200:
            print("✅ Stripe configuration is working!")
            products = response.json()
            print(f"📦 Found {len(products.get('results', []))} products")
            return True
        else:
            print(f"❌ Failed to get products: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error testing Stripe configuration: {e}")
        return False

def test_order_creation():
    """Test creating an order with production Stripe"""
    print("\n🛒 Testing Order Creation...")
    
    # First, get a product to use
    try:
        response = requests.get(PRODUCTS_URL)
        if response.status_code != 200:
            print("❌ Failed to get products for testing")
            return False
            
        products = response.json()
        if not products.get('results'):
            print("❌ No products available for testing")
            return False
            
        product = products['results'][0]
        product_id = product['id']
        
        print(f"📦 Using product: {product['name']} (${product['price_pesos']})")
        
        # Create test order
        order_data = {
            "product_id": product_id,
            "client_name": "Production Test Customer",
            "client_email": "test@example.com",
            "client_phone": "1234567890",
            "client_address": "123 Test St, Test City",
            "currency": "MXN"
        }
        
        response = requests.post(ORDERS_URL, json=order_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Order created successfully!")
            print(f"🆔 Order ID: {result['order_id']}")
            print(f"🔗 Checkout URL: {result['checkout_url']}")
            print(f"📊 Status: {result['status']}")
            
            # Test the checkout URL
            print(f"\n🌐 Test the checkout URL: {result['checkout_url']}")
            print("⚠️  WARNING: This will create a REAL payment session!")
            print("💳 Use Stripe test card: 4242 4242 4242 4242")
            
            return result['order_id']
        else:
            print(f"❌ Failed to create order: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error creating order: {e}")
        return False

def test_webhook_endpoint():
    """Test if webhook endpoint is accessible"""
    print("\n🔗 Testing Webhook Endpoint...")
    
    webhook_url = f"{BASE_URL}/api/webhooks/stripe/"
    
    try:
        response = requests.get(webhook_url)
        
        if response.status_code == 405:  # Method not allowed (expected for GET)
            print("✅ Webhook endpoint is accessible (GET not allowed, which is correct)")
            return True
        elif response.status_code == 404:
            print("❌ Webhook endpoint not found")
            return False
        else:
            print(f"⚠️  Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook endpoint: {e}")
        return False

def check_environment_variables():
    """Check if Stripe environment variables are set"""
    print("\n🔍 Checking Environment Variables...")
    
    publishable_key = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    secret_key = os.environ.get('STRIPE_SECRET_KEY')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    if publishable_key:
        print("✅ STRIPE_PUBLISHABLE_KEY is set")
        if publishable_key.startswith('pk_live_'):
            print("✅ Using PRODUCTION publishable key")
        else:
            print("⚠️  Not using production publishable key")
    else:
        print("❌ STRIPE_PUBLISHABLE_KEY not set")
    
    if secret_key:
        print("✅ STRIPE_SECRET_KEY is set")
        if secret_key.startswith('sk_live_'):
            print("✅ Using PRODUCTION secret key")
        else:
            print("⚠️  Not using production secret key")
    else:
        print("❌ STRIPE_SECRET_KEY not set")
    
    if webhook_secret:
        print("✅ STRIPE_WEBHOOK_SECRET is set")
    else:
        print("⚠️  STRIPE_WEBHOOK_SECRET not set")
    
    return bool(publishable_key and secret_key)

def main():
    print("🚀 Production Stripe Setup Test")
    print("=" * 50)
    
    # Check environment variables
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Environment variables not properly set!")
        print("Please set your Stripe environment variables before testing.")
        return
    
    # Test Stripe configuration
    config_ok = test_stripe_configuration()
    
    if not config_ok:
        print("\n❌ Stripe configuration test failed!")
        return
    
    # Test webhook endpoint
    webhook_ok = test_webhook_endpoint()
    
    if not webhook_ok:
        print("\n⚠️  Webhook endpoint test failed!")
        print("Make sure your webhook endpoint is properly configured.")
    
    # Test order creation
    order_id = test_order_creation()
    
    if order_id:
        print(f"\n🎉 Production Stripe setup is working!")
        print(f"📋 Test order created: {order_id}")
        print("\n📝 Next steps:")
        print("1. Set up production webhook in Stripe Dashboard")
        print("2. Update webhook secret in your settings")
        print("3. Test complete payment flow")
        print("4. Monitor transactions in Stripe Dashboard")
    else:
        print("\n❌ Order creation test failed!")
    
    print("\n" + "=" * 50)
    print("🏁 Testing completed!")

if __name__ == "__main__":
    main()
