#!/usr/bin/env python3
"""
Check Stripe configuration in running Django server
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8000"
PRODUCTS_URL = f"{BASE_URL}/api/products/"

def check_stripe_config():
    """Check if Stripe is properly configured"""
    print("🔧 Checking Stripe Configuration in Running Server...")
    
    try:
        # Test if we can get products (this will use Stripe keys)
        response = requests.get(PRODUCTS_URL)
        
        if response.status_code == 200:
            print("✅ Server is responding!")
            products = response.json()
            print(f"📦 Found {len(products.get('results', []))} products")
            
            # Create a test order to see the checkout URL
            if products.get('results'):
                product = products['results'][0]
                print(f"📦 Testing with product: {product['name']}")
                
                # Create test order
                order_data = {
                    "product_id": product['id'],
                    "client_name": "Test Customer",
                    "client_email": "test@example.com",
                    "client_phone": "1234567890",
                    "client_address": "123 Test St",
                    "currency": "MXN"
                }
                
                order_response = requests.post(f"{BASE_URL}/api/orders/", json=order_data)
                
                if order_response.status_code == 201:
                    result = order_response.json()
                    checkout_url = result.get('checkout_url', '')
                    
                    print(f"🔗 Checkout URL: {checkout_url}")
                    
                    if 'cs_test_' in checkout_url:
                        print("⚠️  WARNING: Still using TEST mode (cs_test_ in URL)")
                        print("🔍 This means Stripe is still in test mode")
                    elif 'cs_live_' in checkout_url:
                        print("✅ SUCCESS: Using LIVE mode (cs_live_ in URL)")
                    else:
                        print("❓ Unknown mode: URL doesn't contain cs_test_ or cs_live_")
                    
                    return checkout_url
                else:
                    print(f"❌ Failed to create order: {order_response.status_code}")
                    print(order_response.text)
                    return None
            else:
                print("❌ No products available for testing")
                return None
        else:
            print(f"❌ Server not responding: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Stripe Configuration Check")
    print("=" * 50)
    
    checkout_url = check_stripe_config()
    
    if checkout_url:
        print(f"\n📝 Checkout URL: {checkout_url}")
        print("\n🔍 Analysis:")
        if 'cs_test_' in checkout_url:
            print("❌ Still in TEST mode - need to fix Stripe configuration")
        elif 'cs_live_' in checkout_url:
            print("✅ In LIVE mode - production ready!")
        else:
            print("❓ Unknown mode - check configuration")
    else:
        print("❌ Could not test Stripe configuration")
    
    print("\n" + "=" * 50)
    print("🏁 Check completed!")
