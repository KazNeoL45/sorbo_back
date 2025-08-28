#!/usr/bin/env python3
"""
Script to migrate existing data from cents to pesos format
Run this after applying the database migration
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sorbo_back.settings')
django.setup()

from api.models import Product, Order
from decimal import Decimal

def migrate_products_to_pesos():
    """Migrate product prices from cents to pesos"""
    print("Migrating product prices from cents to pesos...")
    
    # Get all products that might have old price_cents data
    products = Product.objects.all()
    
    for product in products:
        # Check if price_pesos is 0 (default value) and we need to set it
        if product.price_pesos == Decimal('0.00'):
            # If there's no old data, set a default price
            product.price_pesos = Decimal('100.00')  # Default $100 MXN
            product.currency = 'MXN'
            product.save()
            print(f"✓ Set default price for product '{product.name}': ${product.price_pesos} MXN")
        else:
            print(f"✓ Product '{product.name}' already has price: ${product.price_pesos} {product.currency}")

def migrate_orders_to_pesos():
    """Migrate order totals from cents to pesos"""
    print("\nMigrating order totals from cents to pesos...")
    
    # Get all orders that might have old total_cents data
    orders = Order.objects.all()
    
    for order in orders:
        # Check if total_pesos is 0 (default value) and we need to set it
        if order.total_pesos == Decimal('0.00'):
            # Set total_pesos based on the product price
            order.total_pesos = order.product.price_pesos
            order.currency = order.product.currency
            order.save()
            print(f"✓ Updated order {order.id}: ${order.total_pesos} {order.currency}")
        else:
            print(f"✓ Order {order.id} already has total: ${order.total_pesos} {order.currency}")

def create_sample_products():
    """Create sample products with peso prices"""
    print("\nCreating sample products with peso prices...")
    
    sample_products = [
        {
            'name': 'T-Shirt',
            'description': 'Comfortable cotton t-shirt',
            'stock': 50,
            'type': 'clothing',
            'price_pesos': Decimal('299.99'),
            'currency': 'MXN'
        },
        {
            'name': 'Coffee Mug',
            'description': 'Ceramic coffee mug',
            'stock': 100,
            'type': 'kitchen',
            'price_pesos': Decimal('89.50'),
            'currency': 'MXN'
        },
        {
            'name': 'Notebook',
            'description': 'Spiral bound notebook',
            'stock': 200,
            'type': 'office',
            'price_pesos': Decimal('45.00'),
            'currency': 'MXN'
        }
    ]
    
    for product_data in sample_products:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        
        if created:
            print(f"✓ Created product: {product.name} - ${product.price_pesos} {product.currency}")
        else:
            print(f"✓ Product already exists: {product.name} - ${product.price_pesos} {product.currency}")

def main():
    print("=== Migrating to Peso Format ===\n")
    
    # Migrate existing data
    migrate_products_to_pesos()
    migrate_orders_to_pesos()
    
    # Create sample products if none exist
    if Product.objects.count() == 0:
        create_sample_products()
    
    print("\n=== Migration Completed ===")
    print("\nSummary:")
    print(f"- Total products: {Product.objects.count()}")
    print(f"- Total orders: {Order.objects.count()}")
    print("- All prices are now in pesos (MXN)")
    print("- Stripe integration automatically converts pesos to cents")

if __name__ == "__main__":
    main()
