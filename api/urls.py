from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .views import (
    LoginView, ProductViewSet, OrderViewSet, 
    StripeWebhookView, OrderSuccessView, OrderCancelView, CORSTestView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

def cors_options(request):
    """
    Handle OPTIONS requests for CORS preflight
    """
    response = HttpResponse()
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin"
    response["Access-Control-Max-Age"] = "86400"
    return response

urlpatterns = [
    # CORS preflight handler - must come before router
    path('products/', csrf_exempt(cors_options), name='cors-products'),
    path('orders/', csrf_exempt(cors_options), name='cors-orders'),
    
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    
    # CORS test endpoint
    path('cors-test/', CORSTestView.as_view(), name='cors-test'),
    
    # Order success/cancel pages (must come before router to avoid conflicts)
    path('orders/<uuid:order_id>/success/', OrderSuccessView.as_view(), name='order-success'),
    path('orders/<uuid:order_id>/cancel/', OrderCancelView.as_view(), name='order-cancel'),
    
    # Stripe webhook
    path('stripe/webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    
    # API endpoints
    path('', include(router.urls)),
]
