from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView, ProductViewSet, OrderViewSet, 
    StripeWebhookView, OrderSuccessView, OrderCancelView, CORSTestView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    
    # CORS test endpoint
    path('cors-test/', CORSTestView.as_view(), name='cors-test'),
    
    # Order success/cancel pages (must come before router to avoid conflicts)
    path('orders/success/', OrderSuccessView.as_view(), name='order-success'),
    path('orders/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    
    # Stripe webhook
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # API endpoints
    path('', include(router.urls)),
]
