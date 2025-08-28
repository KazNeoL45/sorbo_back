#!/usr/bin/env python3
"""
Webhook Debug and Test Script
This script helps debug webhook issues and test webhook configuration.
"""

import os
import sys
import django
import stripe
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sorbo_back.settings')
django.setup()

from api.models import Order

def test_webhook_configuration():
    """Test webhook configuration and keys"""
    print("🔧 Testing Webhook Configuration...")
    print("=" * 50)
    
    # Check environment variables
    stripe_pub = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'NOT_SET')
    stripe_sec = os.environ.get('STRIPE_SECRET_KEY', 'NOT_SET')
    webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET', 'NOT_SET')
    
    print(f"STRIPE_PUBLISHABLE_KEY: {'✅ Set' if stripe_pub != 'NOT_SET' else '❌ Not set'}")
    print(f"STRIPE_SECRET_KEY: {'✅ Set' if stripe_sec != 'NOT_SET' else '❌ Not set'}")
    print(f"STRIPE_WEBHOOK_SECRET: {'✅ Set' if webhook_secret != 'NOT_SET' else '❌ Not set'}")
    
    # Check if keys are test keys
    if stripe_pub.startswith('pk_test_'):
        print("✅ Using test keys (correct for development)")
    elif stripe_pub.startswith('pk_live_'):
        print("⚠️  Using live keys (be careful!)")
    else:
        print("❌ Invalid publishable key format")
    
    if stripe_sec.startswith('sk_test_'):
        print("✅ Using test secret key (correct for development)")
    elif stripe_sec.startswith('sk_live_'):
        print("⚠️  Using live secret key (be careful!)")
    else:
        print("❌ Invalid secret key format")
    
    if webhook_secret.startswith('whsec_'):
        print("✅ Valid webhook secret format")
    else:
        print("❌ Invalid webhook secret format")
    
    print()

def test_stripe_connection():
    """Test Stripe API connection"""
    print("🔌 Testing Stripe Connection...")
    print("=" * 50)
    
    try:
        # Test API connection
        stripe.api_key = settings.STRIPE_SECRET_KEY
        account = stripe.Account.retrieve()
        print(f"✅ Stripe connection successful")
        print(f"   Account ID: {account.id}")
        print(f"   Account Type: {account.type}")
        print(f"   Charges Enabled: {account.charges_enabled}")
        print(f"   Payouts Enabled: {account.payouts_enabled}")
        
    except stripe.error.AuthenticationError:
        print("❌ Authentication failed - check your secret key")
    except stripe.error.APIConnectionError:
        print("❌ Connection failed - check your internet connection")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()

def check_pending_orders():
    """Check for orders that might need webhook processing"""
    print("📋 Checking Pending Orders...")
    print("=" * 50)
    
    pending_orders = Order.objects.filter(status='pending')
    success_orders = Order.objects.filter(status='success')
    failed_orders = Order.objects.filter(status='failed')
    
    print(f"Pending orders: {pending_orders.count()}")
    print(f"Success orders: {success_orders.count()}")
    print(f"Failed orders: {failed_orders.count()}")
    
    if pending_orders.exists():
        print("\n📝 Pending orders that might need webhook processing:")
        for order in pending_orders[:5]:  # Show first 5
            print(f"   Order {order.id}: {order.product.name} - {order.created_at}")
            if order.stripe_session_id:
                print(f"     Stripe Session: {order.stripe_session_id}")
                # Try to check session status
                try:
                    session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                    print(f"     Session Status: {session.status}")
                    print(f"     Payment Status: {session.payment_status}")
                except Exception as e:
                    print(f"     ❌ Error checking session: {e}")
            else:
                print(f"     ❌ No Stripe session ID")
            print()
    
    print()

def test_webhook_endpoint():
    """Test webhook endpoint"""
    print("🌐 Testing Webhook Endpoint...")
    print("=" * 50)
    
    webhook_url = "http://127.0.0.1:8000/api/stripe/webhook/"
    print(f"Webhook URL: {webhook_url}")
    print("To test webhooks locally, use Stripe CLI:")
    print("   stripe listen --forward-to localhost:8000/api/stripe/webhook/")
    print()
    print("Or test manually with curl:")
    print("   curl -X POST http://127.0.0.1:8000/api/stripe/webhook/ \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -H 'Stripe-Signature: test_signature' \\")
    print("     -d '{\"test\": \"data\"}'")
    print()

def check_webhook_events():
    """Check what webhook events are configured"""
    print("📡 Webhook Events Configuration...")
    print("=" * 50)
    
    required_events = [
        'checkout.session.completed',
        'checkout.session.expired',
        'checkout.session.async_payment_succeeded',
        'checkout.session.async_payment_failed',
        'payment_intent.succeeded',
        'payment_intent.payment_failed',
        'payment_intent.canceled'
    ]
    
    print("Required webhook events:")
    for event in required_events:
        print(f"   ✅ {event}")
    
    print("\nMake sure these events are configured in your Stripe Dashboard:")
    print("   Dashboard → Developers → Webhooks → Add endpoint")
    print("   URL: http://127.0.0.1:8000/api/stripe/webhook/ (for local testing)")
    print("   Or: https://yourdomain.com/api/stripe/webhook/ (for production)")
    print()

def main():
    """Run all tests"""
    print("🚀 Stripe Webhook Debug Tool")
    print("=" * 60)
    print()
    
    test_webhook_configuration()
    test_stripe_connection()
    check_pending_orders()
    test_webhook_endpoint()
    check_webhook_events()
    
    print("🎯 Next Steps:")
    print("1. If keys are missing, set them in your .env file")
    print("2. If webhook secret is missing, get it from Stripe Dashboard")
    print("3. Configure webhook endpoint in Stripe Dashboard")
    print("4. Use Stripe CLI to test webhooks locally")
    print("5. Check pending orders and manually update if needed")
    print()
    print("For more help, see STRIPE_SETUP.md")

if __name__ == "__main__":
    main()
