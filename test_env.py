#!/usr/bin/env python3
"""
Test script to check if environment variables are loaded from .env file
"""

import os

# Try to load .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded successfully")
except ImportError:
    print("❌ python-dotenv not installed")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

# Check environment variables
print("\n🔍 Environment Variables Check:")
print("=" * 40)

stripe_pub = os.environ.get('STRIPE_PUBLISHABLE_KEY', 'NOT_SET')
stripe_sec = os.environ.get('STRIPE_SECRET_KEY', 'NOT_SET')

print(f"STRIPE_PUBLISHABLE_KEY: {'✅ Set' if stripe_pub != 'NOT_SET' else '❌ Not set'}")
print(f"STRIPE_SECRET_KEY: {'✅ Set' if stripe_sec != 'NOT_SET' else '❌ Not set'}")

if stripe_pub != 'NOT_SET':
    print(f"Publishable key starts with: {stripe_pub[:20]}...")
if stripe_sec != 'NOT_SET':
    print(f"Secret key starts with: {stripe_sec[:20]}...")

# Check if .env file exists
env_file_exists = os.path.exists('.env')
print(f"\n.env file exists: {'✅ Yes' if env_file_exists else '❌ No'}")

if env_file_exists:
    with open('.env', 'r') as f:
        content = f.read()
        print(f"\n.env file content:")
        print("=" * 40)
        print(content)
