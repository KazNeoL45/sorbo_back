# Stripe Setup Guide for SorboBackend

This guide will help you set up Stripe payment processing for your Django REST API.

## 🚀 Quick Setup Steps

### 1. Create Stripe Account
1. Sign up at [stripe.com](https://stripe.com)
2. Complete account verification
3. Access your [Dashboard](https://dashboard.stripe.com)

### 2. Get Your API Keys
1. Go to **Developers → API keys** in Stripe Dashboard
2. Copy your keys:
   - **Publishable key**: `pk_test_...` (test) or `pk_live_...` (live)
   - **Secret key**: `sk_test_...` (test) or `sk_live_...` (live)

### 3. Set Up Environment Variables

Create a `.env` file in your project root:

```bash
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_your_test_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_test_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_test_webhook_secret_here

# Django settings
SECRET_KEY=your_django_secret_key_here
DEBUG=True
```

### 4. Install python-dotenv (Optional)

```bash
pip install python-dotenv
```

Then add to your `settings.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

### 5. Set Up Webhook Endpoint

1. **In Stripe Dashboard**: Go to **Developers → Webhooks**
2. **Add endpoint**: `https://yourdomain.com/api/stripe/webhook/`
3. **Select events**:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. **Copy webhook secret**: Starts with `whsec_...`

### 6. Test Your Setup

#### Test with curl:

```bash
# 1. Login to get JWT token
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "s0rb0mx24", "password": "s0rb0s0rb1t0"}'

# 2. Create an order (replace TOKEN and PRODUCT_ID)
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "YOUR_PRODUCT_UUID",
    "buyer_full_name": "John Doe",
    "buyer_address": "123 Main St, City, Country",
    "total_cents": 2999,
    "currency": "USD"
  }'
```

## 🔧 Configuration Details

### Development vs Production

**Development (Test Mode):**
- Use test keys (`pk_test_`, `sk_test_`)
- Test with Stripe's test card numbers
- No real charges

**Production (Live Mode):**
- Use live keys (`pk_live_`, `sk_live_`)
- Real payments processed
- Requires account verification

### Test Card Numbers

Use these for testing:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires authentication**: `4000 0025 0000 3155`

### Webhook Testing

For local development, use [Stripe CLI](https://stripe.com/docs/stripe-cli):

```bash
# Install Stripe CLI
stripe listen --forward-to localhost:8000/api/stripe/webhook/
```

## 🛡️ Security Best Practices

1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Verify webhook signatures** (already implemented)
4. **Use HTTPS** in production
5. **Test thoroughly** before going live

## 📋 API Endpoints

### Public Endpoints (No Auth Required)
- `GET /api/products/` - List all products
- `GET /api/products/{id}/` - Get specific product

### Authenticated Endpoints (Auth Required)
- `POST /api/orders/` - Create order & Stripe checkout
- `GET /api/orders/` - List orders (Admin)
- `GET /api/orders/{id}/status/` - Get order status

### Stripe Webhook
- `POST /api/stripe/webhook/` - Handle payment events

## 🔍 Troubleshooting

### Common Issues:

1. **"Invalid API key"**
   - Check your secret key is correct
   - Ensure you're using test keys for development

2. **"Webhook signature verification failed"**
   - Verify webhook secret is correct
   - Check webhook endpoint URL

3. **"Order not found"**
   - Ensure product exists in database
   - Check product UUID format

4. **"Payment failed"**
   - Use test card numbers
   - Check Stripe Dashboard for error details

### Debug Mode:

Enable debug logging in `settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'stripe': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## 📞 Support

- **Stripe Documentation**: [stripe.com/docs](https://stripe.com/docs)
- **Stripe Support**: [support.stripe.com](https://support.stripe.com)
- **API Reference**: [stripe.com/docs/api](https://stripe.com/docs/api)
