#!/usr/bin/env python3
"""
Fix Pending Orders Script
This script manually updates orders that are pending but actually paid.
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

def fix_pending_orders():
    """Fix orders that are pending but actually paid"""
    print("🔧 Fixing Pending Orders...")
    print("=" * 50)
    
    pending_orders = Order.objects.filter(status='pending')
    fixed_count = 0
    
    for order in pending_orders:
        if not order.stripe_session_id:
            print(f"❌ Order {order.id}: No Stripe session ID")
            continue
            
        try:
            # Check Stripe session status
            session = stripe.checkout.Session.retrieve(order.stripe_session_id)
            
            if session.payment_status == 'paid' and session.status == 'complete':
                # Update order status
                order.status = 'success'
                order.save()
                
                # Reduce product stock
                product = order.product
                if product.stock > 0:
                    product.stock -= 1
                    product.save()
                    print(f"✅ Fixed Order {order.id}: {product.name} - Stock reduced to {product.stock}")
                else:
                    print(f"⚠️  Fixed Order {order.id}: {product.name} - No stock left")
                
                fixed_count += 1
            else:
                print(f"⏳ Order {order.id}: Payment status = {session.payment_status}, Session status = {session.status}")
                
        except stripe.error.StripeError as e:
            print(f"❌ Error checking order {order.id}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error with order {order.id}: {e}")
    
    print(f"\n🎉 Fixed {fixed_count} orders!")
    print()
    
    # Show final status
    pending_count = Order.objects.filter(status='pending').count()
    success_count = Order.objects.filter(status='success').count()
    failed_count = Order.objects.filter(status='failed').count()
    
    print("📊 Final Order Status:")
    print(f"   Pending: {pending_count}")
    print(f"   Success: {success_count}")
    print(f"   Failed: {failed_count}")

def main():
    """Main function"""
    print("🚀 Fix Pending Orders Tool")
    print("=" * 60)
    print()
    
    # Test Stripe connection first
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        account = stripe.Account.retrieve()
        print(f"✅ Connected to Stripe account: {account.id}")
    except Exception as e:
        print(f"❌ Stripe connection failed: {e}")
        return
    
    print()
    
    # Fix pending orders
    fix_pending_orders()
    
    print("\n🎯 Next Steps:")
    print("1. Set up webhook secret in your .env file")
    print("2. Configure webhook endpoint in Stripe Dashboard")
    print("3. Enable charges and payouts in your Stripe account")
    print("4. Test the success page again")

if __name__ == "__main__":
    main()
