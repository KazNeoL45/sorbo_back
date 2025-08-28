# Webhook Setup and Troubleshooting Guide

## 🚨 Current Issues Fixed

✅ **Orders are now properly updated** - All pending orders that were actually paid have been fixed
✅ **Success page now shows beautiful HTML** - No more JSON responses
✅ **Cancel page now shows proper HTML** - User-friendly cancellation page

## 🔧 Remaining Issues to Fix

### 1. Webhook Secret Configuration

**Problem**: `STRIPE_WEBHOOK_SECRET` is not set, so webhooks can't be processed.

**Solution**:

1. **Get Webhook Secret from Stripe Dashboard**:
   - Go to [Stripe Dashboard](https://dashboard.stripe.com)
   - Navigate to **Developers → Webhooks**
   - Click **Add endpoint**
   - Set URL to: `http://127.0.0.1:8000/api/stripe/webhook/` (for local testing)
   - Select these events:
     - `checkout.session.completed`
     - `checkout.session.expired`
     - `checkout.session.async_payment_succeeded`
     - `checkout.session.async_payment_failed`
     - `payment_intent.succeeded`
     - `payment_intent.payment_failed`
     - `payment_intent.canceled`
   - Click **Add endpoint**
   - Copy the **Signing secret** (starts with `whsec_`)

2. **Add to Environment Variables**:
   ```bash
   # In your .env file
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### 2. Stripe Account Activation

**Problem**: Charges and payouts are disabled in your Stripe account.

**Solution**:
1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Complete account verification
3. Enable charges and payouts
4. Add business information
5. Verify your identity

### 3. Local Webhook Testing

**For Local Development**:

1. **Install Stripe CLI**:
   ```bash
   # Windows (using Chocolatey)
   choco install stripe-cli
   
   # Or download from: https://github.com/stripe/stripe-cli/releases
   ```

2. **Login to Stripe**:
   ```bash
   stripe login
   ```

3. **Forward Webhooks**:
   ```bash
   stripe listen --forward-to localhost:8000/api/stripe/webhook/
   ```

4. **Test Webhooks**:
   ```bash
   stripe trigger checkout.session.completed
   ```

## 🧪 Testing Your Setup

### 1. Test Webhook Configuration
```bash
python test_webhook_debug.py
```

### 2. Test Order Creation and Payment
```bash
# 1. Create an order
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "YOUR_PRODUCT_UUID",
    "client_name": "John Doe",
    "client_email": "john@example.com",
    "client_phone": "1234567890",
    "client_address": "123 Main St, City, Country",
    "currency": "MXN"
  }'

# 2. Use the checkout_url to complete payment
# 3. Check the success page
```

### 3. Test Success Page
Visit: `http://localhost:8000/api/orders/{order_id}/success/`

You should see a beautiful success page with:
- ✅ Green checkmark icon
- Order details
- Success message
- "Volver al Inicio" button

### 4. Test Cancel Page
Visit: `http://localhost:8000/api/orders/{order_id}/cancel/`

You should see a cancel page with:
- ❌ Red X icon
- Order details
- Cancel message
- Navigation buttons

## 🔍 Debugging Tools

### 1. Webhook Debug Script
```bash
python test_webhook_debug.py
```
This script checks:
- Environment variables
- Stripe connection
- Pending orders
- Webhook configuration

### 2. Fix Pending Orders Script
```bash
python fix_pending_orders.py
```
This script manually updates orders that are pending but actually paid.

### 3. Manual Order Status Check
```bash
# Check specific order status
curl http://localhost:8000/api/orders/{order_id}/status/

# Check Stripe session status
curl http://localhost:8000/api/orders/{order_id}/check_stripe_status/
```

## 📋 Checklist

- [ ] Set `STRIPE_WEBHOOK_SECRET` in `.env` file
- [ ] Configure webhook endpoint in Stripe Dashboard
- [ ] Enable charges and payouts in Stripe account
- [ ] Test webhook forwarding with Stripe CLI
- [ ] Test order creation and payment flow
- [ ] Verify success page displays correctly
- [ ] Verify cancel page displays correctly
- [ ] Check that orders update automatically via webhooks

## 🆘 Common Issues

### Issue: "Invalid signature" error
**Solution**: Check that webhook secret is correct and matches Stripe Dashboard

### Issue: Orders stay pending after payment
**Solution**: 
1. Check webhook secret is set
2. Verify webhook endpoint is accessible
3. Use `fix_pending_orders.py` to manually update

### Issue: Success page shows JSON instead of HTML
**Solution**: The fix has been applied - restart your Django server

### Issue: "Charges disabled" error
**Solution**: Complete Stripe account verification and enable charges

## 🎯 Next Steps

1. **Set up webhook secret** (most important)
2. **Enable Stripe account** for real payments
3. **Test complete payment flow**
4. **Monitor webhook logs** for any issues
5. **Deploy to production** when ready

## 📞 Support

- **Stripe Documentation**: [stripe.com/docs](https://stripe.com/docs)
- **Stripe Support**: [support.stripe.com](https://support.stripe.com)
- **Webhook Testing**: [stripe.com/docs/webhooks/test](https://stripe.com/docs/webhooks/test)

