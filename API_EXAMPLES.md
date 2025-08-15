# SorboBackend API Usage Examples

This document provides practical examples of how to use the SorboBackend API using curl commands.

## Prerequisites

1. Make sure the Django server is running: `python manage.py runserver`
2. The server should be accessible at `http://localhost:8000`

## Authentication

### Login to get JWT token

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "s0rb0mx24",
    "password": "s0rb0s0rb1t0"
  }'
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "username": "s0rb0mx24",
    "is_staff": true
  }
}
```

**Save the access token for subsequent requests:**
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Products

### List all products (Public - no authentication required)

```bash
curl -X GET http://localhost:8000/api/products/
```

### Get a specific product (Public - no authentication required)

```bash
curl -X GET http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000/
```

### Create a new product (Admin only)

```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "name": "Sample Product",
    "description": "This is a sample product description",
    "stock": 10,
    "type": "electronics",
    "price_cents": 2999,
    "currency": "USD"
  }'
```

### Update a product (Admin only)

```bash
curl -X PUT http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Updated Product Name",
    "description": "Updated product description",
    "stock": 15,
    "type": "electronics",
    "price_cents": 3499,
    "currency": "USD"
  }'
```

### Delete a product (Admin only)

```bash
curl -X DELETE http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000/ \
  -H "Authorization: Bearer $TOKEN"
```

## Orders

### Create a new order

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "buyer_full_name": "John Doe",
    "buyer_address": "123 Main Street, City, Country",
    "total_cents": 2999,
    "currency": "USD"
  }'
```

**Response:**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440001",
  "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
  "session_id": "cs_test_..."
}
```

### Get order status

```bash
curl -X GET http://localhost:8000/api/orders/550e8400-e29b-41d4-a716-446655440001/status/ \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "order_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### List all orders (Admin only)

```bash
curl -X GET http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer $TOKEN"
```

## Stripe Integration

### Webhook endpoint (for Stripe to call)

```bash
curl -X POST http://localhost:8000/api/stripe/webhook/ \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: t=1234567890,v1=..." \
  -d '{
    "type": "checkout.session.completed",
    "data": {
      "object": {
        "id": "cs_test_...",
        "payment_status": "paid"
      }
    }
  }'
```

### Order success page (Public)

```bash
curl -X GET http://localhost:8000/api/orders/success/
```

### Order cancel page (Public)

```bash
curl -X GET http://localhost:8000/api/orders/cancel/
```

## Complete Workflow Example

Here's a complete example of creating a product and order:

```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "s0rb0mx24", "password": "s0rb0s0rb1t0"}' | \
  jq -r '.access_token')

echo "Token: $TOKEN"

# 2. Create a product
PRODUCT_RESPONSE=$(curl -s -X POST http://localhost:8000/api/products/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "name": "Test Product",
    "description": "A test product",
    "stock": 10,
    "type": "test",
    "price_cents": 1999,
    "currency": "USD"
  }')

PRODUCT_ID=$(echo $PRODUCT_RESPONSE | jq -r '.id')
echo "Created product: $PRODUCT_ID"

# 3. Create an order
ORDER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"product_id\": \"$PRODUCT_ID\",
    \"buyer_full_name\": \"Test User\",
    \"buyer_address\": \"123 Test St\",
    \"total_cents\": 1999,
    \"currency\": \"USD\"
  }")

ORDER_ID=$(echo $ORDER_RESPONSE | jq -r '.order_id')
CHECKOUT_URL=$(echo $ORDER_RESPONSE | jq -r '.checkout_url')
echo "Created order: $ORDER_ID"
echo "Checkout URL: $CHECKOUT_URL"

# 4. Check order status
curl -s -X GET http://localhost:8000/api/orders/$ORDER_ID/status/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

## Error Handling

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Example error response

```json
{
  "error": "Invalid credentials"
}
```

## Notes

1. **Base64 Images**: The `picture` field expects base64-encoded images with the format: `data:image/jpeg;base64,<base64_string>`

2. **Stripe Integration**: For full Stripe functionality, you need to:
   - Configure valid Stripe API keys in `settings.py`
   - Set up webhook endpoints in your Stripe dashboard
   - Use HTTPS in production for webhook security

3. **CORS**: The API is configured to allow all origins in development. For production, configure specific allowed origins.

4. **Authentication**: The hardcoded credentials are for development only. In production, implement proper user authentication.

5. **Database**: The project uses SQLite by default. For production, consider using PostgreSQL.
