import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from .models import Product, Order
from .serializers import ProductSerializer, ProductCreateUpdateSerializer, OrderSerializer, OrderCreateSerializer
from .permissions import IsAuthenticatedOrReadOnly, IsAdminUser
import time
import uuid
import hashlib
import base64
import json


def reduce_product_stock(product, quantity=1):
    """
    Reduce product stock by the specified quantity
    Returns True if successful, False if insufficient stock
    """
    if product.stock >= quantity:
        product.stock -= quantity
        product.save()
        return True
    return False

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderPagination(PageNumberPagination):
    """
    Custom pagination for orders
    """
    page_size = 50  # Show 50 orders per page
    page_size_query_param = 'page_size'  # Allow client to override page size
    max_page_size = 100  # Maximum 100 orders per page
    page_query_param = 'page'  # Page number parameter


class LoginView(APIView):
    """
    Hardcoded authentication view that returns simple tokens
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if (username == settings.HARDCODED_USERNAME and
            password == settings.HARDCODED_PASSWORD):

            # Create a dummy user for token generation
            from django.contrib.auth.models import User
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'is_staff': True, 'is_superuser': True}
            )

            # Generate simple tokens without using JWT library
            timestamp = int(time.time())
            
            # Create access token payload
            access_payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': timestamp + 3600,  # 1 hour
                'type': 'access'
            }
            
            # Create refresh token payload
            refresh_payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': timestamp + 86400,  # 24 hours
                'type': 'refresh'
            }
            
            # Encode tokens as base64 strings
            access_token_str = base64.b64encode(
                json.dumps(access_payload).encode('utf-8')
            ).decode('utf-8')
            
            refresh_token_str = base64.b64encode(
                json.dumps(refresh_payload).encode('utf-8')
            ).decode('utf-8')

            return Response({
                'access_token': access_token_str,
                'refresh_token': refresh_token_str,
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
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        # Allow public access for read operations (list and retrieve)
        return []  # No permissions required for read operations
    
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
    pagination_class = OrderPagination
    
    def get_permissions(self):
        """
        Allow public access for order creation and retrieval, require auth for other operations
        """
        if self.action in ['create', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order with pending status and initiate Stripe checkout
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Get the product
        product = Product.objects.get(id=serializer.validated_data['product_id'])
        
        # Create order with pending status first
        order_data = serializer.validated_data.copy()
        order = Order.objects.create(**order_data)
        
        # Create Stripe checkout session
        try:
            # Convert pesos to cents for Stripe (Stripe requires amounts in cents)
            price_cents = int(float(product.price_pesos) * 100)
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': serializer.validated_data['currency'].lower(),
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': price_cents,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{settings.FRONTEND_URL}?order_id={order.id}&status=success',
                cancel_url=f'{settings.FRONTEND_URL}?order_id={order.id}&status=cancel',
                metadata={
                    'order_id': str(order.id),
                    'product_id': str(product.id),
                    'client_name': serializer.validated_data['client_name'],
                    'client_email': serializer.validated_data['client_email'],
                }
            )
            
            # Update order with Stripe session ID
            order.stripe_session_id = checkout_session.id
            order.save()
            
            return Response({
                'order_id': str(order.id),
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'status': order.status
            }, status=status.HTTP_201_CREATED)
            
        except stripe.error.StripeError as e:
            # If Stripe fails, mark order as failed
            order.status = 'failed'
            order.save()
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def list(self, request, *args, **kwargs):
        """
        Get all orders (requires authentication)
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
        Get order by ID (public access - customers can view their orders)
        """
        return super().retrieve(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Update order (admin only) - allows status updates
        """
        try:
            order = self.get_object()
            new_status = request.data.get('status')
            
            if new_status:
                # Validate status
                valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
                if new_status not in valid_statuses:
                    return Response({
                        'error': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Check status transition rules
                current_status = order.status
                if current_status == 'pending' and new_status not in ['success', 'failed', 'cancelled']:
                    return Response({
                        'error': f'Cannot change status from "{current_status}" to "{new_status}". Pending orders can only be changed to success, failed, or cancelled.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if current_status == 'success' and new_status not in ['sent', 'shipped', 'delivered']:
                    return Response({
                        'error': f'Cannot change status from "{current_status}" to "{new_status}". Success orders can only be changed to sent, shipped, or delivered.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if current_status == 'sent' and new_status not in ['shipped', 'delivered']:
                    return Response({
                        'error': f'Cannot change status from "{current_status}" to "{new_status}". Sent orders can only be changed to shipped or delivered.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if current_status == 'shipped' and new_status != 'delivered':
                    return Response({
                        'error': f'Cannot change status from "{current_status}" to "{new_status}". Shipped orders can only be changed to delivered.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                if current_status in ['failed', 'cancelled', 'delivered']:
                    return Response({
                        'error': f'Cannot change status from "{current_status}". This status is final.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update the order
            old_status = order.status
            serializer = self.get_serializer(order, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response({
                'order_id': str(order.id),
                'old_status': old_status,
                'new_status': order.status,
                'message': f'Order updated successfully',
                'updated_at': order.updated_at,
                'order': serializer.data
            })
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
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
    
    @action(detail=True, methods=['post'])
    def check_stripe_status(self, request, pk=None):
        """
        Manually check and update order status based on Stripe session status
        """
        try:
            order = self.get_object()
            
            if not order.stripe_session_id:
                return Response({
                    'error': 'No Stripe session ID found for this order'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the checkout session from Stripe
            try:
                session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                
                # Update order status based on Stripe session status
                if session.payment_status == 'paid':
                    # Only update if not already success to avoid duplicate stock reduction
                    if order.status != 'success':
                        order.status = 'success'
                        order.save()
                        
                        # Reduce product stock
                        product = order.product
                        if reduce_product_stock(product, 1):
                            print(f"Order {order.id} marked as success - stock reduced for product {product.name} (new stock: {product.stock})")
                        else:
                            print(f"Warning: Order {order.id} completed but product {product.name} has no stock left")
                    
                    message = f"Order status updated to success - payment completed"
                elif session.payment_status == 'unpaid':
                    if session.status == 'expired':
                        order.status = 'failed'
                        order.save()
                        message = f"Order status updated to failed - session expired"
                    else:
                        message = f"Order still pending - payment status: {session.payment_status}, session status: {session.status}"
                else:
                    message = f"Unknown payment status: {session.payment_status}"
                
                return Response({
                    'order_id': str(order.id),
                    'stripe_session_id': order.stripe_session_id,
                    'stripe_payment_status': session.payment_status,
                    'stripe_session_status': session.status,
                    'order_status': order.status,
                    'message': message
                })
                
            except stripe.error.StripeError as e:
                return Response({
                    'error': f'Stripe error: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_sent(self, request, pk=None):
        """
        Mark order as sent (admin only)
        """
        try:
            order = self.get_object()
            
            # Check if order is in a valid state to be marked as sent
            if order.status not in ['success']:
                return Response({
                    'error': f'Order must be in "success" status to be marked as sent. Current status: {order.status}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update order status to sent
            order.status = 'sent'
            order.save()
            
            return Response({
                'order_id': str(order.id),
                'status': order.status,
                'message': f'Order marked as sent successfully',
                'updated_at': order.updated_at
            })
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['patch', 'put'])
    def update_status(self, request, pk=None):
        """
        Update order status (admin only)
        """
        try:
            order = self.get_object()
            new_status = request.data.get('status')
            
            if not new_status:
                return Response({
                    'error': 'Status field is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate status
            valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
            if new_status not in valid_statuses:
                return Response({
                    'error': f'Invalid status. Valid statuses are: {", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check status transition rules
            current_status = order.status
            if current_status == 'pending' and new_status not in ['success', 'failed', 'cancelled']:
                return Response({
                    'error': f'Cannot change status from "{current_status}" to "{new_status}". Pending orders can only be changed to success, failed, or cancelled.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if current_status == 'success' and new_status not in ['sent', 'shipped', 'delivered']:
                return Response({
                    'error': f'Cannot change status from "{current_status}" to "{new_status}". Success orders can only be changed to sent, shipped, or delivered.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if current_status == 'sent' and new_status not in ['shipped', 'delivered']:
                return Response({
                    'error': f'Cannot change status from "{current_status}" to "{new_status}". Sent orders can only be changed to shipped or delivered.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if current_status == 'shipped' and new_status != 'delivered':
                return Response({
                    'error': f'Cannot change status from "{current_status}" to "{new_status}". Shipped orders can only be changed to delivered.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if current_status in ['failed', 'cancelled', 'delivered']:
                return Response({
                    'error': f'Cannot change status from "{current_status}". This status is final.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update order status
            old_status = order.status
            order.status = new_status
            order.save()
            
            return Response({
                'order_id': str(order.id),
                'old_status': old_status,
                'new_status': order.status,
                'message': f'Order status updated from "{old_status}" to "{new_status}" successfully',
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
    Handle Stripe webhooks for checkout session status updates
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
        
        # Handle checkout session events
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self.handle_checkout_session_completed(session)
        elif event['type'] == 'checkout.session.expired':
            session = event['data']['object']
            self.handle_checkout_session_expired(session)
        elif event['type'] == 'checkout.session.async_payment_succeeded':
            session = event['data']['object']
            self.handle_checkout_session_completed(session)
        elif event['type'] == 'checkout.session.async_payment_failed':
            session = event['data']['object']
            self.handle_checkout_session_failed(session)
        # Handle payment intent events as backup
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            self.handle_payment_intent_succeeded(payment_intent)
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            self.handle_payment_intent_failed(payment_intent)
        elif event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
            self.handle_payment_intent_canceled(payment_intent)
        
        return Response({'status': 'success'})
    
    def handle_checkout_session_completed(self, session):
        """
        Handle successful checkout session completion
        """
        try:
            order = Order.objects.get(stripe_session_id=session.id)
            
            # Only update if not already success to avoid duplicate stock reduction
            if order.status != 'success':
                order.status = 'success'
                order.save()
                
                # Reduce product stock
                product = order.product
                if reduce_product_stock(product, 1):
                    print(f"✅ Webhook: Order {order.id} marked as success - stock reduced for product {product.name} (new stock: {product.stock})")
                else:
                    print(f"⚠️  Warning: Order {order.id} completed but product {product.name} has no stock left")
            else:
                print(f"ℹ️  Order {order.id} already marked as success, skipping duplicate update")
                
        except Order.DoesNotExist:
            print(f"❌ Error: Order not found for session {session.id}")
        except Exception as e:
            print(f"❌ Error handling checkout session completed: {e}")
    
    def handle_checkout_session_expired(self, session):
        """
        Handle expired checkout session
        """
        try:
            order = Order.objects.get(stripe_session_id=session.id)
            order.status = 'failed'
            order.save()
            print(f"❌ Webhook: Order {order.id} marked as failed - checkout session expired")
        except Order.DoesNotExist:
            print(f"❌ Error: Order not found for session {session.id}")
        except Exception as e:
            print(f"❌ Error handling checkout session expired: {e}")
    
    def handle_checkout_session_failed(self, session):
        """
        Handle failed checkout session (async payment failed)
        """
        try:
            order = Order.objects.get(stripe_session_id=session.id)
            order.status = 'failed'
            order.save()
            print(f"❌ Webhook: Order {order.id} marked as failed - async payment failed")
        except Order.DoesNotExist:
            print(f"❌ Error: Order not found for session {session.id}")
        except Exception as e:
            print(f"❌ Error handling checkout session failed: {e}")
    
    def handle_payment_intent_succeeded(self, payment_intent):
        """
        Handle successful payment intent (backup method)
        """
        try:
            # Try to find order by session ID first
            if payment_intent.get('metadata', {}).get('order_id'):
                order = Order.objects.get(id=payment_intent['metadata']['order_id'])
                
                # Only update if not already success to avoid duplicate stock reduction
                if order.status != 'success':
                    order.status = 'success'
                    order.save()
                    
                    # Reduce product stock
                    product = order.product
                    if reduce_product_stock(product, 1):
                        print(f"✅ Payment Intent: Order {order.id} marked as success - stock reduced for product {product.name} (new stock: {product.stock})")
                    else:
                        print(f"⚠️  Warning: Order {order.id} completed but product {product.name} has no stock left")
                else:
                    print(f"ℹ️  Order {order.id} already marked as success, skipping duplicate update")
                    
            else:
                # Try to find by session ID if available
                session_id = payment_intent.get('metadata', {}).get('session_id')
                if session_id:
                    order = Order.objects.get(stripe_session_id=session_id)
                    
                    # Only update if not already success to avoid duplicate stock reduction
                    if order.status != 'success':
                        order.status = 'success'
                        order.save()
                        
                        # Reduce product stock
                        product = order.product
                        if reduce_product_stock(product, 1):
                            print(f"✅ Payment Intent: Order {order.id} marked as success - stock reduced for product {product.name} (new stock: {product.stock})")
                        else:
                            print(f"⚠️  Warning: Order {order.id} completed but product {product.name} has no stock left")
                    else:
                        print(f"ℹ️  Order {order.id} already marked as success, skipping duplicate update")
                        
        except Order.DoesNotExist:
            print(f"❌ Error: Order not found for payment intent {payment_intent.id}")
        except Exception as e:
            print(f"❌ Error handling payment intent succeeded: {e}")
    
    def handle_payment_intent_failed(self, payment_intent):
        """
        Handle failed payment intent (backup method)
        """
        try:
            # Try to find order by session ID first
            if payment_intent.get('metadata', {}).get('order_id'):
                order = Order.objects.get(id=payment_intent['metadata']['order_id'])
                order.status = 'failed'
                order.save()
                print(f"Order {order.id} marked as failed - payment intent failed")
            else:
                # Try to find by session ID if available
                session_id = payment_intent.get('metadata', {}).get('session_id')
                if session_id:
                    order = Order.objects.get(stripe_session_id=session_id)
                    order.status = 'failed'
                    order.save()
                    print(f"Order {order.id} marked as failed - payment intent failed (via session)")
        except Order.DoesNotExist:
            print(f"Order not found for payment intent {payment_intent.id}")
        except Exception as e:
            print(f"Error handling payment intent failed: {e}")
    
    def handle_payment_intent_canceled(self, payment_intent):
        """
        Handle canceled payment intent (backup method)
        """
        try:
            # Try to find order by session ID first
            if payment_intent.get('metadata', {}).get('order_id'):
                order = Order.objects.get(id=payment_intent['metadata']['order_id'])
                order.status = 'failed'
                order.save()
                print(f"Order {order.id} marked as failed - payment intent canceled")
            else:
                # Try to find by session ID if available
                session_id = payment_intent.get('metadata', {}).get('session_id')
                if session_id:
                    order = Order.objects.get(stripe_session_id=session_id)
                    order.status = 'failed'
                    order.save()
                    print(f"Order {order.id} marked as failed - payment intent canceled (via session)")
        except Order.DoesNotExist:
            print(f"Order not found for payment intent {payment_intent.id}")
        except Exception as e:
            print(f"Error handling payment intent canceled: {e}")


class OrderSuccessView(APIView):
    """
    Handle successful order completion - Returns JSON for frontend handling
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            
            # If order is still pending, check Stripe session status
            if order.status == 'pending' and order.stripe_session_id:
                try:
                    session = stripe.checkout.Session.retrieve(order.stripe_session_id)
                    if session.payment_status == 'paid':
                        # Update order status and reduce stock
                        if order.status != 'success':
                            order.status = 'success'
                            order.save()
                            
                            # Reduce product stock
                            product = order.product
                            if reduce_product_stock(product, 1):
                                print(f"✅ Success Page: Order {order.id} marked as success - stock reduced for product {product.name} (new stock: {product.stock})")
                            else:
                                print(f"⚠️  Warning: Order {order.id} completed but product {product.name} has no stock left")
                except stripe.error.StripeError as e:
                    print(f"❌ Error checking Stripe session: {e}")
            
            # Return JSON response instead of HTML
            return Response({
                'success': True,
                'message': 'Order completed successfully',
                'order': {
                    'id': str(order.id),
                    'status': order.status,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'product': {
                        'name': order.product.name,
                        'price_pesos': str(order.product.price_pesos),
                        'currency': order.product.currency,
                        'current_stock': order.product.stock
                    },
                    'client_name': order.client_name,
                    'client_email': order.client_email
                },
                'redirect_url': '/success'  # Frontend route to redirect to
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


class OrderCancelView(APIView):
    """
    Handle cancelled orders - Returns JSON for frontend handling
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            # Mark order as failed if cancelled
            if order.status == 'pending':
                order.status = 'failed'
                order.save()
            
            # Return JSON response instead of HTML
            return Response({
                'success': False,
                'message': 'Order was cancelled',
                'order': {
                    'id': str(order.id),
                    'status': order.status,
                    'created_at': order.created_at,
                    'updated_at': order.updated_at,
                    'product': {
                        'name': order.product.name,
                        'price_pesos': str(order.product.price_pesos),
                        'currency': order.product.currency
                    },
                    'client_name': order.client_name,
                    'client_email': order.client_email
                },
                'redirect_url': '/cancel'  # Frontend route to redirect to
            }, status=status.HTTP_200_OK)
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


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
