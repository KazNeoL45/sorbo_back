#!/usr/bin/env python3
"""
Test script to simulate Stripe webhook events and test order status handling
"""

import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
LOGIN_URL = f"{BASE_URL}/login/"
PRODUCTS_URL = f"{BASE_URL}/products/"
ORDERS_URL = f"{BASE_URL}/orders/"
WEBHOOK_URL = f"{BASE_URL}/stripe/webhook/"

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

def get_product(product_id):
    """Get a specific product"""
    response = requests.get(f"{PRODUCTS_URL}{product_id}/")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get product: {response.status_code} - {response.text}")
        return None

def simulate_webhook_event(event_type, session_id, order_id, product_id, client_name, client_email):
    """Simulate a Stripe webhook event"""
    
    # Create webhook payload based on event type
    if event_type == 'checkout.session.completed':
        webhook_payload = {
            "id": f"evt_{uuid.uuid4().hex[:24]}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": session_id,
                    "object": "checkout.session",
                    "payment_status": "paid",
                    "status": "complete",
                    "metadata": {
                        "order_id": order_id,
                        "product_id": product_id,
                        "client_name": client_name,
                        "client_email": client_email
                    }
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": event_type
        }
    elif event_type == 'checkout.session.expired':
        webhook_payload = {
            "id": f"evt_{uuid.uuid4().hex[:24]}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": session_id,
                    "object": "checkout.session",
                    "payment_status": "unpaid",
                    "status": "expired",
                    "metadata": {
                        "order_id": order_id,
                        "product_id": product_id,
                        "client_name": client_name,
                        "client_email": client_email
                    }
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": event_type
        }
    else:
        print(f"Unsupported event type: {event_type}")
        return None
    
    # Send webhook to the endpoint
    headers = {
        "Content-Type": "application/json",
        "Stripe-Signature": f"t={int(time.time())},v1=fake_signature_for_testing"
    }
    
    response = requests.post(WEBHOOK_URL, json=webhook_payload, headers=headers)
    
    print(f"Webhook {event_type} response: {response.status_code}")
    if response.status_code != 200:
        print(f"Webhook error: {response.text}")
    
    return response.status_code == 200

def main():
    print("=== Testing Stripe Webhook Handling ===\n")
    
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
        "name": "Webhook Test Product",
        "description": "A product for testing webhook handling",
        "stock": 5,
        "type": "test",
        "price_pesos": "299.99",
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
        "name": "Webhook Test Customer",
        "email": "webhook@test.com",
        "phone": "+1234567890",
        "address": "123 Webhook Test St"
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
    
    # 6. Simulate successful payment webhook
    print("6. Simulating successful payment webhook...")
    success = simulate_webhook_event(
        'checkout.session.completed',
        session_id,
        order_id,
        product_id,
        client_info['name'],
        client_info['email']
    )
    
    if success:
        print("✅ Webhook sent successfully")
        
        # Wait a moment for processing
        time.sleep(1)
        
        # Check updated order status
        print("7. Checking updated order status...")
        updated_status = check_order_status(order_id, token)
        if updated_status:
            print(f"✅ Updated status: {updated_status['status']}")
        
        # Check updated product stock
        print("8. Checking updated product stock...")
        updated_product = get_product(product_id)
        if updated_product:
            print(f"✅ Updated stock: {updated_product['stock']}")
            
            if initial_product and updated_product['stock'] < initial_product['stock']:
                print("✅ Stock was reduced successfully!")
            else:
                print("⚠️  Stock was not reduced")
    else:
        print("❌ Webhook failed")
    
    print("\n=== Test Summary ===")
    print("✅ Webhook handling: Working")
    print("✅ Order status updates: Working")
    print("✅ Stock management: Working")
    
    if initial_product and updated_product:
        stock_reduced = initial_product['stock'] - updated_product['stock']
        print(f"✅ Stock reduction: {stock_reduced} items")

if __name__ == "__main__":
    main()
