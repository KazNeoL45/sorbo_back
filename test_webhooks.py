#!/usr/bin/env python3
"""
Test script for Stripe webhook functionality
This script helps test webhook events and verify order status updates
"""

import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8000/api"
WEBHOOK_URL = f"{BASE_URL}/stripe/webhook/"
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

def get_order_status(order_id, token):
    """Get order status"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{ORDERS_URL}{order_id}/status/", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get order status: {response.status_code}")
        return None

def simulate_webhook_event(event_type, session_id, order_id=None):
    """
    Simulate a Stripe webhook event
    Note: This is for testing purposes only. In production, Stripe sends real webhooks.
    """
    
    # Sample webhook payloads for different event types
    webhook_payloads = {
        'checkout.session.completed': {
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
                        "order_id": order_id
                    } if order_id else {}
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": "checkout.session.completed"
        },
        'checkout.session.expired': {
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
                        "order_id": order_id
                    } if order_id else {}
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": "checkout.session.expired"
        },
        'payment_intent.succeeded': {
            "id": f"evt_{uuid.uuid4().hex[:24]}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": f"pi_{uuid.uuid4().hex[:24]}",
                    "object": "payment_intent",
                    "status": "succeeded",
                    "metadata": {
                        "order_id": order_id,
                        "session_id": session_id
                    } if order_id else {}
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": "payment_intent.succeeded"
        },
        'payment_intent.payment_failed': {
            "id": f"evt_{uuid.uuid4().hex[:24]}",
            "object": "event",
            "api_version": "2020-08-27",
            "created": int(time.time()),
            "data": {
                "object": {
                    "id": f"pi_{uuid.uuid4().hex[:24]}",
                    "object": "payment_intent",
                    "status": "requires_payment_method",
                    "last_payment_error": {
                        "type": "card_error",
                        "code": "card_declined",
                        "message": "Your card was declined."
                    },
                    "metadata": {
                        "order_id": order_id,
                        "session_id": session_id
                    } if order_id else {}
                }
            },
            "livemode": False,
            "pending_webhooks": 1,
            "request": {
                "id": f"req_{uuid.uuid4().hex[:24]}",
                "idempotency_key": None
            },
            "type": "payment_intent.payment_failed"
        }
    }
    
    if event_type not in webhook_payloads:
        print(f"Unknown event type: {event_type}")
        return False
    
    payload = webhook_payloads[event_type]
    
    # Send webhook to the endpoint
    headers = {
        'Content-Type': 'application/json',
        'Stripe-Signature': 't=1234567890,v1=fake_signature_for_testing'
    }
    
    response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        print(f"✓ Webhook {event_type} sent successfully")
        return True
    else:
        print(f"✗ Failed to send webhook {event_type}: {response.status_code} - {response.text}")
        return False

def test_webhook_flow():
    """Test the complete webhook flow"""
    print("=== Testing Stripe Webhook Flow ===\n")
    
    # 1. Login
    print("1. Logging in...")
    token = login()
    if not token:
        print("Login failed. Please check your credentials.")
        return
    print("✓ Login successful\n")
    
    # 2. Get an existing order (you need to create one first)
    print("2. Getting existing orders...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(ORDERS_URL, headers=headers)
    
    if response.status_code != 200 or not response.json():
        print("No orders found. Please create an order first using test_order_system.py")
        return
    
    orders = response.json()
    order = orders[0]  # Use the first order
    order_id = order['id']
    session_id = order.get('stripe_session_id', f'cs_test_{uuid.uuid4().hex[:24]}')
    
    print(f"✓ Using order: {order_id}")
    print(f"  Session ID: {session_id}")
    print(f"  Current status: {order['status']}")
    print()
    
    # 3. Test different webhook events
    print("3. Testing webhook events...")
    
    # Test successful payment
    print("Testing checkout.session.completed...")
    if simulate_webhook_event('checkout.session.completed', session_id, order_id):
        time.sleep(1)  # Wait a moment for processing
        status = get_order_status(order_id, token)
        if status:
            print(f"  Order status after webhook: {status['status']}")
    
    print()
    
    # Test failed payment
    print("Testing payment_intent.payment_failed...")
    if simulate_webhook_event('payment_intent.payment_failed', session_id, order_id):
        time.sleep(1)  # Wait a moment for processing
        status = get_order_status(order_id, token)
        if status:
            print(f"  Order status after webhook: {status['status']}")
    
    print()
    
    # Test expired session
    print("Testing checkout.session.expired...")
    if simulate_webhook_event('checkout.session.expired', session_id, order_id):
        time.sleep(1)  # Wait a moment for processing
        status = get_order_status(order_id, token)
        if status:
            print(f"  Order status after webhook: {status['status']}")
    
    print()
    
    print("=== Webhook Testing Completed ===")
    print("\nNote: This script simulates webhook events for testing purposes.")
    print("In production, Stripe sends real webhooks to your webhook endpoint.")

if __name__ == "__main__":
    test_webhook_flow()
