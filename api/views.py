import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Order
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, OrderSerializer, OrderCreateSerializer
from .permissions import IsAuthenticatedOrReadOnly, IsAdminUser

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class LoginView(APIView):
    """
    Hardcoded authentication view that returns JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if (username == settings.HARDCODED_USERNAME and 
            password == settings.HARDCODED_PASSWORD):
            
            # Create a dummy user for JWT token generation
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'is_staff': True, 'is_superuser': True}
            )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': {
                    'username': user.username,
                    'is_staff': user.is_staff
                }
            })
        
        return Response(
            {'error': 'Invalid credentials'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticatedOrReadOnly()]
    
    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductSerializer
    
    def list(self, request, *args, **kwargs):
        """
        Public endpoint to list all products
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Public endpoint to retrieve a specific product
        """
        return super().retrieve(request, *args, **kwargs)


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Order operations
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order and initiate Stripe checkout
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the product
        product = Product.objects.get(id=serializer.validated_data['product_id'])
        
        # Create Stripe checkout session
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': serializer.validated_data['currency'].lower(),
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': serializer.validated_data['total_cents'],
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/api/orders/success/'),
                cancel_url=request.build_absolute_uri('/api/orders/cancel/'),
                metadata={
                    'product_id': str(product.id),
                    'buyer_name': serializer.validated_data['buyer_full_name'],
                    'buyer_address': serializer.validated_data['buyer_address'],
                }
            )
            
            # Create order with Stripe session ID
            order_data = serializer.validated_data.copy()
            order_data['stripe_session_id'] = checkout_session.id
            order = Order.objects.create(**order_data)
            
            return Response({
                'order_id': str(order.id),
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get order status
        """
        try:
            order = self.get_object()
            return Response({
                'order_id': str(order.id),
                'status': order.status,
                'created_at': order.created_at,
                'updated_at': order.updated_at
            })
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """
    Handle Stripe webhooks
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            return Response(
                {'error': 'Invalid payload'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError as e:
            return Response(
                {'error': 'Invalid signature'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_session_completed(session)
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_intent_succeeded(payment_intent)
        
        return Response({'status': 'success'})
    
    def handle_checkout_session_completed(self, session):
        """
        Handle successful checkout session completion
        """
        try:
            order = Order.objects.get(stripe_session_id=session.id)
            order.status = 'paid'
            order.save()
        except Order.DoesNotExist:
            pass
    
    def handle_payment_intent_succeeded(self, payment_intent):
        """
        Handle successful payment intent
        """
        # You can add additional logic here if needed
        pass


class OrderSuccessView(APIView):
    """
    Handle successful order completion
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Order completed successfully!',
            'status': 'success'
        })


class OrderCancelView(APIView):
    """
    Handle cancelled orders
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'Order was cancelled.',
            'status': 'cancelled'
        })


class CORSTestView(APIView):
    """
    Test endpoint for CORS debugging
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        return Response({
            'message': 'CORS is working!',
            'status': 'success',
            'origin': request.META.get('HTTP_ORIGIN', 'No origin header'),
            'method': request.method
        })
    
    def post(self, request):
        return Response({
            'message': 'CORS POST is working!',
            'status': 'success',
            'data': request.data,
            'origin': request.META.get('HTTP_ORIGIN', 'No origin header')
        })
    
    def options(self, request):
        response = Response()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
