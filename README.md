# SorboBackend - Django REST API

A comprehensive Django REST API backend with JWT authentication, product management, Stripe integration, and order tracking.

## Features

- **JWT Authentication** with hardcoded credentials
- **Product CRUD** operations with UUID primary keys
- **Base64 image support** for product pictures
- **Stripe Checkout integration** for payments
- **Order tracking** with status management
- **Public/protected API endpoints**
- **CORS support** for frontend integration

## Project Structure

```
sorbo_back/
├── manage.py
├── requirements.txt
├── README.md
├── sorbo_back/          # Project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── api/                 # API app
    ├── __init__.py
    ├── models.py        # Product & Order models
    ├── views.py         # API views
    ├── urls.py          # App routes
    ├── serializers.py   # DRF serializers
    ├── permissions.py   # Custom permissions
    └── admin.py         # Django admin
```

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sorbo_back
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Configure Stripe (required for payments)**
   Edit `sorbo_back/settings.py` and update:
   ```python
   STRIPE_PUBLISHABLE_KEY = 'your_stripe_publishable_key'
   STRIPE_SECRET_KEY = 'your_stripe_secret_key'
   STRIPE_WEBHOOK_SECRET = 'your_stripe_webhook_secret'
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication

#### Login
- **URL:** `POST /api/login/`
- **Description:** Authenticate with hardcoded credentials
- **Request Body:**
  ```json
  {
    "username": "s0rb0mx24",
    "password": "s0rb0s0rb1t0"
  }
  ```
- **Response:**
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

### Products

#### List Products (Public)
- **URL:** `GET /api/products/`
- **Description:** Get all products (no authentication required)
- **Response:**
  ```json
  {
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
        "name": "Sample Product",
        "description": "Product description",
        "stock": 10,
        "type": "electronics",
        "price_cents": 2999,
        "currency": "USD",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
  ```

#### Get Product (Public)
- **URL:** `GET /api/products/{id}/`
- **Description:** Get specific product details (no authentication required)

#### Create Product (Admin Only)
- **URL:** `POST /api/products/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Request Body:**
  ```json
  {
    "picture": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
    "name": "New Product",
    "description": "Product description",
    "stock": 10,
    "type": "electronics",
    "price_cents": 2999,
    "currency": "USD"
  }
  ```

#### Update Product (Admin Only)
- **URL:** `PUT /api/products/{id}/`
- **Headers:** `Authorization: Bearer <access_token>`

#### Delete Product (Admin Only)
- **URL:** `DELETE /api/products/{id}/`
- **Headers:** `Authorization: Bearer <access_token>`

### Orders

#### Create Order
- **URL:** `POST /api/orders/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Request Body:**
  ```json
  {
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "buyer_full_name": "John Doe",
    "buyer_address": "123 Main St, City, Country",
    "total_cents": 2999,
    "currency": "USD"
  }
  ```
- **Response:**
  ```json
  {
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_...",
    "session_id": "cs_test_..."
  }
  ```

#### List Orders (Admin Only)
- **URL:** `GET /api/orders/`
- **Headers:** `Authorization: Bearer <access_token>`

#### Get Order Status
- **URL:** `GET /api/orders/{id}/status/`
- **Headers:** `Authorization: Bearer <access_token>`
- **Response:**
  ```json
  {
    "order_id": "550e8400-e29b-41d4-a716-446655440001",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
  ```

### Stripe Integration

#### Webhook Handler
- **URL:** `POST /api/stripe/webhook/`
- **Description:** Handles Stripe webhook events for payment status updates

#### Order Success Page
- **URL:** `GET /api/orders/success/`
- **Description:** Redirect page after successful payment

#### Order Cancel Page
- **URL:** `GET /api/orders/cancel/`
- **Description:** Redirect page after cancelled payment

## Models

### Product Model
```python
class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    picture = models.TextField()  # base64 image
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock = models.PositiveIntegerField()
    type = models.CharField(max_length=100)
    price_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Order Model
```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    buyer_full_name = models.CharField(max_length=255)
    buyer_address = models.TextField()
    stripe_session_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

## Authentication

The API uses hardcoded authentication credentials:
- **Username:** `s0rb0mx24`
- **Password:** `s0rb0s0rb1t0`

Upon successful login, the API returns JWT tokens that should be included in subsequent requests as:
```
Authorization: Bearer <access_token>
```

## Permissions

- **Public endpoints:** Product listing and retrieval
- **Authenticated endpoints:** Order creation and status checking
- **Admin endpoints:** Product CRUD operations, order management

## Stripe Configuration

1. **Get your Stripe keys** from the Stripe Dashboard
2. **Update settings.py** with your keys:
   ```python
   STRIPE_PUBLISHABLE_KEY = 'pk_test_...'
   STRIPE_SECRET_KEY = 'sk_test_...'
   STRIPE_WEBHOOK_SECRET = 'whsec_...'
   ```
3. **Configure webhook endpoint** in Stripe Dashboard:
   - URL: `https://yourdomain.com/api/stripe/webhook/`
   - Events: `checkout.session.completed`, `payment_intent.succeeded`

## Development

### Running Tests
```bash
python manage.py test
```

### Creating Migrations
```bash
python manage.py makemigrations api
```

### Applying Migrations
```bash
python manage.py migrate
```

### Django Admin
Access the admin interface at `http://localhost:8000/admin/` with your superuser credentials.

## Dependencies

- Django 5.2.5
- Django REST Framework 3.14.0
- djangorestframework-simplejwt 5.3.0
- drf-extra-fields 3.4.0
- stripe 7.8.0
- django-cors-headers 4.3.1
- psycopg2-binary 2.9.9
- Pillow 10.1.0

## Environment Variables

For production, consider using environment variables for sensitive settings:

```python
import os

SECRET_KEY = os.environ.get('SECRET_KEY')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
```

## License

This project is licensed under the MIT License.
