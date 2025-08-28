# Order System Documentation

## Overview

The order system has been updated to include comprehensive client information and improved status management. Orders are created with a `pending` status and change to `success` or `failed` based on the payment outcome.

**Important**: All prices are now displayed in **pesos (MXN)** instead of cents for better user experience. The system automatically converts pesos to cents for Stripe integration.

## Key Features

### 1. Client Information
When creating an order, the following client information is required:
- **client_name**: Full name of the client
- **client_email**: Email address of the client
- **client_phone**: Phone number of the client
- **client_address**: Complete address of the client

### 2. Stock Management
- **Stock Validation**: Orders cannot be created for products with zero stock
- **Automatic Stock Reduction**: Product stock is automatically reduced by 1 when payment is successful
- **Stock Monitoring**: Current stock levels are displayed in order responses
- **Out of Stock Prevention**: System prevents creating orders for out-of-stock products

### 3. Order Status Flow
- **pending**: Initial status when order is created
- **success**: Payment completed successfully (stock reduced)
- **failed**: Payment failed or was cancelled
- **sent**: Order has been sent to customer (admin can update)
- **shipped**: Order has been shipped (admin can update)
- **delivered**: Order has been delivered (admin can update)
- **cancelled**: Order was cancelled (admin can update)

### 3. Order Creation Process
1. Order is created with `pending` status
2. Stripe checkout session is created
3. Client is redirected to Stripe checkout
4. Webhook updates order status based on payment outcome

### 4. Price Format
- **API Response**: Prices in pesos (e.g., `"25.50"` for $25.50 MXN)
- **Database Storage**: Decimal field with 2 decimal places
- **Stripe Integration**: Automatic conversion from pesos to cents
- **Currency**: Default is MXN (Mexican Peso)

## Pagination

The order system uses pagination to efficiently handle large numbers of orders:

### Default Settings
- **Orders per page**: 50 (default)
- **Maximum per page**: 100
- **Pagination type**: Page Number Pagination

### How to Control Pagination

#### 1. Using Query Parameters
```
GET /api/orders/?page=1&page_size=25
```

- `page`: Page number (starts from 1)
- `page_size`: Number of orders per page (1-100)

#### 2. Examples
```bash
# Get first 25 orders
GET /api/orders/?page_size=25

# Get second page with 50 orders
GET /api/orders/?page=2&page_size=50

# Get all orders (up to 100 per page)
GET /api/orders/?page_size=100
```

#### 3. Response Format
```json
{
    "count": 150,           // Total number of orders
    "next": "http://...",   // URL for next page (null if no next page)
    "previous": "http://...", // URL for previous page (null if no previous page)
    "results": [...]        // Array of orders for current page
}
```

### Performance Considerations
- **Recommended page size**: 25-50 orders for optimal performance
- **Maximum page size**: 100 orders to prevent server overload
- **Total orders**: Unlimited (depends on database size)

## API Endpoints

### 1. Create Order
**POST** `/api/orders/`

**Request Body:**
```json
{
    "product_id": "uuid-of-product",
    "client_name": "John Doe",
    "client_email": "john.doe@example.com",
    "client_phone": "+1234567890",
    "client_address": "123 Main St, City, State 12345"
}
```

**Response:**
```json
{
    "order_id": "uuid-of-order",
    "checkout_url": "https://checkout.stripe.com/...",
    "session_id": "cs_test_...",
    "status": "pending"
}
```

### 2. Get All Orders
**GET** `/api/orders/`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Number of orders per page (default: 50, max: 100)

**Example:** `GET /api/orders/?page=1&page_size=25`

**Response:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/orders/?page=2&page_size=25",
    "previous": null,
    "results": [
        {
            "id": "uuid-of-order",
            "product": {
                "id": "uuid-of-product",
                "name": "Product Name",
                "description": "Product Description",
                "price_pesos": "25.00",
                "currency": "MXN"
            },
            "client_name": "John Doe",
            "client_email": "john.doe@example.com",
            "client_phone": "+1234567890",
            "client_address": "123 Main St, City, State 12345",
            "status": "success",
            "total_pesos": "25.00",
            "currency": "MXN",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:05:00Z"
        }
    ]
}
```

### 3. Get Order by ID
**GET** `/api/orders/{order_id}/`

**Headers:** None required (public access)

**Response:** Same as individual order object in the list above

### 4. Get Order Status
**GET** `/api/orders/{order_id}/status/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "order_id": "uuid-of-order",
    "status": "success",
    "created_at": "2024-01-01T12:00:00Z",
    "updated_at": "2024-01-01T12:05:00Z"
}
```

### 5. Order Success Page
**GET** `/api/orders/{order_id}/success/`

**Response:**
```json
{
    "message": "Order completed successfully!",
    "order_id": "uuid-of-order",
    "status": "success",
    "product": {
        "name": "Product Name",
        "current_stock": 24,
        "price_pesos": "25.00",
        "currency": "MXN"
    },
    "total_pesos": "25.00",
    "currency": "MXN"
}
```

### 6. Order Cancel Page
**GET** `/api/orders/{order_id}/cancel/`

**Response:**
```json
{
    "message": "Order was cancelled.",
    "order_id": "uuid-of-order",
    "status": "failed"
}
```

### 7. Mark Order as Sent
**POST** `/api/orders/{order_id}/mark_as_sent/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "order_id": "uuid-of-order",
    "status": "sent",
    "message": "Order marked as sent successfully",
    "updated_at": "2024-01-01T12:10:00Z"
}
```

**Requirements:**
- Order must be in "success" status
- Requires admin authentication
- Only successful orders can be marked as sent

## Database Schema

### Order Model
```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('sent', 'Sent'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Client information
    client_name = models.CharField(max_length=255, default='')
    client_email = models.EmailField(default='')
    client_phone = models.CharField(max_length=20, default='')
    client_address = models.TextField(default='')
    
    # Order details
    stripe_session_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_pesos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='MXN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Stock Management

The system automatically manages product stock levels:

### Stock Validation
- Orders cannot be created for products with zero stock
- The system validates stock availability before creating orders
- Error message: `"Product 'Product Name' is out of stock. Available stock: 0"`

### Automatic Stock Reduction
- When a payment is successful, product stock is automatically reduced by 1
- Stock reduction happens in both webhook handlers:
  - `checkout.session.completed`
  - `payment_intent.succeeded` (backup method)
- Stock levels are updated in real-time

### Stock Monitoring
- Current stock levels are displayed in order success responses
- Product stock information is included in order details
- Stock levels are visible in product listings

## Webhook Handling

The system handles the following Stripe webhook events to automatically update order status and manage stock:

### Key Features
- **Automatic Order Status Updates**: Orders are automatically updated based on Stripe payment status
- **Stock Management**: Product stock is automatically reduced when payments are successful
- **Duplicate Prevention**: System prevents duplicate stock reductions for the same order
- **Comprehensive Logging**: All webhook events are logged with clear status indicators
- **Error Handling**: Robust error handling for webhook processing failures

### Webhook Events Handled

### Checkout Session Events (Primary)
1. **checkout.session.completed**
   - Updates order status to `success`
   - Reduces product stock by 1
   - Triggered when payment is completed successfully
   - Logs: `✅ Webhook: Order {id} marked as success - stock reduced for product {name} (new stock: {stock})`

2. **checkout.session.expired**
   - Updates order status to `failed`
   - Triggered when checkout session expires without payment
   - Logs: `❌ Webhook: Order {id} marked as failed - checkout session expired`

3. **checkout.session.async_payment_succeeded**
   - Updates order status to `success`
   - Reduces product stock by 1
   - Triggered for asynchronous payment methods (bank transfers, etc.)
   - Same handling as `checkout.session.completed`

4. **checkout.session.async_payment_failed**
   - Updates order status to `failed`
   - Triggered when async payment fails
   - Logs: `❌ Webhook: Order {id} marked as failed - async payment failed`

### Payment Intent Events (Backup)
5. **payment_intent.succeeded**
   - Updates order status to `success`
   - Reduces product stock by 1
   - Backup method if checkout session events are missed
   - Logs: `✅ Payment Intent: Order {id} marked as success - stock reduced for product {name} (new stock: {stock})`

6. **payment_intent.payment_failed**
   - Updates order status to `failed`
   - Backup method for failed payments
   - Logs: `❌ Payment Intent: Order {id} marked as failed - payment failed`

7. **payment_intent.canceled**
   - Updates order status to `failed`
   - Backup method for canceled payments
   - Logs: `❌ Payment Intent: Order {id} marked as failed - payment canceled`

### Manual Status Check
**POST** `/api/orders/{order_id}/check_stripe_status/`

**Headers:** `Authorization: Bearer <token>`

**Response:**
```json
{
    "order_id": "uuid-of-order",
    "stripe_session_id": "cs_test_...",
    "stripe_payment_status": "paid",
    "stripe_session_status": "complete",
    "order_status": "success",
    "message": "Order status updated to success - payment completed"
}
```

This endpoint allows manual checking and updating of order status based on the current Stripe session status. It also includes stock reduction when the payment is successful, making it useful for:
- Debugging webhook issues
- Handling edge cases where webhooks fail
- Manual order status updates
- Testing payment flows

### Duplicate Prevention
The system includes safeguards to prevent duplicate stock reductions:
- Orders are only updated if they're not already in `success` status
- Stock is only reduced once per successful order
- Clear logging indicates when duplicate updates are skipped

## Testing

### Order System Testing
Use the provided `test_order_system.py` script to test the order system:

```bash
python test_order_system.py
```

The script will:
1. Login to get an access token
2. Get available products
3. Create a test order with client information
4. Retrieve order details by ID
5. Check order status
6. List all orders

### Stock Management Testing
Use the provided `test_stock_management.py` script to test stock management:

```bash
python test_stock_management.py
```

The script will:
1. Create a product with limited stock
2. Create multiple orders to test stock validation
3. Verify stock reduction behavior
4. Test order success page with stock information

### Webhook Testing
Use the provided `test_stripe_webhooks.py` script to test webhook handling:

```bash
python test_stripe_webhooks.py
```

The script will:
1. Create a test product and order
2. Simulate Stripe webhook events
3. Verify order status updates
4. Check stock reduction after successful payments

### Manual Status Check Testing
Use the provided `test_manual_status_check.py` script to test manual status checking:

```bash
python test_manual_status_check.py
```

The script will:
1. Create a test product and order
2. Test manual status check functionality
3. Verify order status updates
4. Check stock management integration

## Authentication

All admin endpoints require authentication using JWT tokens. To get a token:

**POST** `/api/login/`

```json
{
    "username": "admin",
    "password": "admin123"
}
```

Response:
```json
{
    "access_token": "your_jwt_token_here",
    "refresh_token": "your_refresh_token_here",
    "user": {
        "username": "admin",
        "is_staff": true
    }
}
```

Include the token in the Authorization header:
```
Authorization: Bearer your_jwt_token_here
```

## Order Status Management

### Order Status Flow

The order system supports the following status transitions:

1. **pending** → **success** (payment completed)
2. **pending** → **failed** (payment failed)
3. **pending** → **cancelled** (order cancelled)
4. **success** → **sent** (order shipped)
5. **success** → **shipped** (order shipped)
6. **success** → **delivered** (order delivered)
7. **sent** → **shipped** (order shipped)
8. **sent** → **delivered** (order delivered)
9. **shipped** → **delivered** (order delivered)

Final statuses (cannot be changed):
- **failed**
- **cancelled** 
- **delivered**

### Update Order Status

**PATCH** `/api/orders/{order_id}/`

Update order status using the standard PATCH method:

```json
{
    "status": "sent"
}
```

Response:
```json
{
    "order_id": "e9473f90-5873-4b81-932a-109fa0ac438c",
    "old_status": "success",
    "new_status": "sent",
    "message": "Order updated successfully",
    "updated_at": "2025-08-26T16:20:00.000000Z",
    "order": {
        "id": "e9473f90-5873-4b81-932a-109fa0ac438c",
        "status": "sent",
        "client_name": "Maxim Alexander Lamas",
        "client_email": "neodarwin45@outlook.com",
        "product": {
            "id": "f3e188cf-3a11-4e1a-9574-712d3c0a6dcd",
            "name": "Product Name",
            "price_pesos": "3000.00"
        }
    }
}
```

### Dedicated Status Update Endpoint

**PATCH** `/api/orders/{order_id}/update_status/`

Alternative endpoint specifically for status updates:

```json
{
    "status": "sent"
}
```

Response:
```json
{
    "order_id": "e9473f90-5873-4b81-932a-109fa0ac438c",
    "old_status": "success",
    "new_status": "sent",
    "message": "Order status updated from \"success\" to \"sent\" successfully",
    "updated_at": "2025-08-26T16:20:00.000000Z"
}
```

### Mark Order as Sent (Legacy)

**POST** `/api/orders/{order_id}/mark_as_sent/`

Legacy endpoint that specifically marks an order as "sent":

```json
{}
```

Response:
```json
{
    "order_id": "e9473f90-5873-4b81-932a-109fa0ac438c",
    "status": "sent",
    "message": "Order marked as sent successfully",
    "updated_at": "2025-08-26T16:20:00.000000Z"
}
```

## Error Handling

### Invalid Status Transition

If you try to change to an invalid status:

```json
{
    "error": "Cannot change status from \"success\" to \"pending\". Success orders can only be changed to sent, shipped, or delivered."
}
```

### Invalid Status Value

If you provide an invalid status:

```json
{
    "error": "Invalid status. Valid statuses are: pending, success, failed, sent, shipped, delivered, cancelled"
}
```

### Final Status Error

If you try to change a final status:

```json
{
    "error": "Cannot change status from \"delivered\". This status is final."
}
```

## Testing Status Updates

Use the provided test script to verify status update functionality:

```bash
python test_status_update.py
```

This script will:
1. Login and get authentication token
2. Find orders with "success" status
3. Test various status transitions
4. Test invalid transitions
5. Test both PATCH and dedicated endpoints

## API Endpoints Summary

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PATCH | `/api/orders/{id}/` | Update order (including status) | Yes |
| PATCH | `/api/orders/{id}/update_status/` | Update order status only | Yes |
| POST | `/api/orders/{id}/mark_as_sent/` | Mark order as sent (legacy) | Yes |
| GET | `/api/orders/{id}/status/` | Get order status | No |
| POST | `/api/orders/{id}/check_stripe_status/` | Check Stripe payment status | Yes |

## Status Update Examples

### Frontend Integration

```javascript
// Update order status
async function updateOrderStatus(orderId, newStatus) {
    const response = await fetch(`/api/orders/${orderId}/`, {
        method: 'PATCH',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: newStatus
        })
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log('Status updated:', result.message);
        return result;
    } else {
        const error = await response.json();
        console.error('Update failed:', error.error);
        throw new Error(error.error);
    }
}

// Usage examples
await updateOrderStatus('e9473f90-5873-4b81-932a-109fa0ac438c', 'sent');
await updateOrderStatus('e9473f90-5873-4b81-932a-109fa0ac438c', 'shipped');
await updateOrderStatus('e9473f90-5873-4b81-932a-109fa0ac438c', 'delivered');
```

### cURL Examples

```bash
# Update to sent status
curl -X PATCH \
  http://localhost:8000/api/orders/e9473f90-5873-4b81-932a-109fa0ac438c/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "sent"}'

# Update to shipped status
curl -X PATCH \
  http://localhost:8000/api/orders/e9473f90-5873-4b81-932a-109fa0ac438c/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'

# Update to delivered status
curl -X PATCH \
  http://localhost:8000/api/orders/e9473f90-5873-4b81-932a-109fa0ac438c/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "delivered"}'
```

## Troubleshooting

### Common Issues

1. **UUID Format**: Order IDs are UUIDs, not integers
2. **Authentication**: Make sure you're using a valid JWT token
3. **Status Transitions**: Follow the allowed status flow
4. **Content-Type**: Always use `application/json` for requests

### Debug Steps

1. Check the order exists: `GET /api/orders/{id}/`
2. Verify current status
3. Check allowed transitions
4. Ensure authentication is working
5. Review error messages for specific issues

## Migration Notes

The existing database has been migrated to include the new client information fields. Existing orders will have empty strings for the new fields, which can be updated manually if needed.

## Security Considerations

1. Client information is stored securely in the database
2. Stripe session IDs are validated before processing
3. Webhook signatures are verified to prevent tampering
4. Authentication is required for sensitive operations
5. Input validation is performed on all client data
