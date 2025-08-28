# Production Stripe Setup Guide

This guide covers setting up Stripe for production with your live keys.

## 🔑 Production Keys

Your production Stripe keys have been configured:

- **Publishable Key**: `pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE`
- **Secret Key**: `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`

## ⚠️ Important Security Notes

### 1. Never Commit Secret Keys
- The secret key (`sk_live_...`) should NEVER be committed to version control
- Use environment variables in production
- Keep the secret key secure and private

### 2. Environment Variables (Recommended)
Set these as environment variables instead of hardcoding:

```bash
# Linux/Mac
export STRIPE_PUBLISHABLE_KEY="pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE"
export STRIPE_SECRET_KEY="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"

# Windows PowerShell
$env:STRIPE_PUBLISHABLE_KEY="pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE"
$env:STRIPE_SECRET_KEY="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"
```

### 3. .env File (Alternative)
Create a `.env` file in your project root:

```env
STRIPE_PUBLISHABLE_KEY=pk_live_51RwX1ZD5cS3MsYULZSr3llAYXLKnKilkngejZwXl2dsIcU6qDpA2C5AMb1X6ciq2WoJQLxEo9UBlZhuHPiOkchul00jygswABE
STRIPE_SECRET_KEY=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
STRIPE_WEBHOOK_SECRET=whsec_your_production_webhook_secret_here
```

**Important**: Add `.env` to your `.gitignore` file!

## 🌐 Production Webhook Setup

### 1. Set Up Production Webhook

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click "Add endpoint"
3. Set the endpoint URL to your production domain:
   ```
   https://your-domain.com/api/webhooks/stripe/
   ```
4. Select these events:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `checkout.session.async_payment_succeeded`
   - `checkout.session.async_payment_failed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`

### 2. Get Webhook Secret

After creating the webhook, copy the signing secret and update your settings:

```python
STRIPE_WEBHOOK_SECRET = "whsec_your_actual_production_webhook_secret"
```

## 🔧 Production Configuration Updates

### 1. Update Frontend URLs

Update your Django settings for production:

```python
# Production URLs
STRIPE_SUCCESS_URL = 'https://your-frontend-domain.com/success'
STRIPE_CANCEL_URL = 'https://your-frontend-domain.com/cancel'
FRONTEND_URL = 'https://your-frontend-domain.com'
```

### 2. Update CORS Settings

For production, restrict CORS to your actual domains:

```python
CORS_ALLOWED_ORIGINS = [
    "https://your-frontend-domain.com",
    "https://www.your-frontend-domain.com",
]

# Remove or set to False for production
CORS_ALLOW_ALL_ORIGINS = False
```

### 3. Security Settings

```python
# Production security settings
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Use HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

## 🧪 Testing Production Setup

### 1. Test Order Creation

```bash
curl -X POST http://your-domain.com/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "your-product-uuid",
    "client_name": "Test Customer",
    "client_email": "test@example.com",
    "client_phone": "1234567890",
    "client_address": "123 Test St, Test City",
    "currency": "MXN"
  }'
```

### 2. Test Webhook (Using Stripe CLI)

```bash
# Install Stripe CLI
stripe listen --forward-to https://your-domain.com/api/webhooks/stripe/

# In another terminal, trigger a test event
stripe trigger checkout.session.completed
```

### 3. Verify Payment Flow

1. Create an order through your API
2. Complete payment on Stripe checkout
3. Verify webhook updates order status
4. Check order status in your admin panel

## 📊 Monitoring Production

### 1. Stripe Dashboard

Monitor these in your Stripe Dashboard:
- **Payments**: Track successful/failed payments
- **Webhooks**: Check webhook delivery status
- **Logs**: Review API request logs
- **Disputes**: Handle chargebacks

### 2. Django Admin

Monitor in Django Admin:
- Order status changes
- Stock updates
- Customer information

### 3. Error Monitoring

Set up error monitoring for:
- Webhook failures
- Payment processing errors
- Database issues

## 🔒 Security Checklist

- [ ] Secret key is not in version control
- [ ] Webhook endpoint is HTTPS
- [ ] Webhook signature verification is enabled
- [ ] CORS is properly configured
- [ ] DEBUG is set to False
- [ ] SSL/HTTPS is enabled
- [ ] Environment variables are used
- [ ] .env file is in .gitignore

## 🚨 Important Warnings

### 1. Live Payments
- **These are REAL payments** - customers will be charged actual money
- Test thoroughly before going live
- Monitor transactions carefully

### 2. Webhook Reliability
- Webhooks are critical for order status updates
- Set up webhook retry logic
- Monitor webhook delivery failures

### 3. Error Handling
- Implement proper error handling for failed payments
- Have a plan for partial failures
- Monitor for edge cases

## 📞 Support

If you encounter issues:

1. Check Stripe Dashboard logs
2. Review Django application logs
3. Verify webhook configuration
4. Test with Stripe CLI
5. Contact Stripe support if needed

## 🔄 Migration from Test to Live

If migrating from test mode:

1. Update all keys to live keys
2. Set up production webhooks
3. Update frontend URLs
4. Test complete payment flow
5. Monitor first few transactions
6. Update documentation

---

**Remember**: Production Stripe keys handle real money. Always test thoroughly and monitor closely!
