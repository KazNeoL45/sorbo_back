from rest_framework import serializers
from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    picture = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'picture', 'name', 'description', 'stock', 
            'type', 'price_pesos', 'currency', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """
        Custom representation to handle empty picture fields
        """
        data = super().to_representation(instance)
        # If picture is empty or None, return empty string instead of null
        if not data.get('picture'):
            data['picture'] = ""
        return data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products with base64 image validation
    """
    picture = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'picture', 'name', 'description', 'stock', 
            'type', 'price_pesos', 'currency'
        ]
    
    def validate_picture(self, value):
        """
        Validate that the picture field contains a valid base64 image if provided
        """
        if value and value.strip():
            # Check if it's a valid base64 image format
            if not value.startswith('data:image/'):
                raise serializers.ValidationError("Picture must be a valid base64 image starting with 'data:image/'")
            
            # Basic validation for base64 format
            try:
                import base64
                # Extract the base64 part after the comma
                if ',' in value:
                    base64_part = value.split(',')[1]
                    # Try to decode to check if it's valid base64
                    base64.b64decode(base64_part)
                else:
                    raise serializers.ValidationError("Invalid base64 image format")
            except Exception:
                raise serializers.ValidationError("Invalid base64 image data")
        
        return value


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'product', 'product_id', 'client_name', 'client_email', 'client_phone', 'client_address',
            'stripe_session_id', 'status', 'total_pesos', 'currency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'stripe_session_id', 'status', 'created_at', 'updated_at']

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        try:
            product = Product.objects.get(id=product_id)
            validated_data['product'] = product
            return super().create(validated_data)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")


class OrderCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField()
    
    class Meta:
        model = Order
        fields = [
            'product_id', 'client_name', 'client_email', 'client_phone', 'client_address'
        ]

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
    
    def validate(self, data):
        """
        Validate order data and set total_pesos and currency from product
        """
        product_id = data.get('product_id')
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                
                # Check if product has sufficient stock
                if product.stock <= 0:
                    raise serializers.ValidationError(
                        f"Product '{product.name}' is out of stock. Available stock: {product.stock}"
                    )
                
                # Set total_pesos and currency from product
                data['total_pesos'] = product.price_pesos
                data['currency'] = product.currency
                
                # Check if amount meets Stripe minimum requirements (convert to cents for validation)
                price_cents = int(float(product.price_pesos) * 100)
                if product.currency.upper() == 'MXN' and price_cents < 1000:
                    raise serializers.ValidationError(
                        f"Amount must be at least $10.00 MXN. Current amount: ${product.price_pesos} MXN"
                    )
                
            except Product.DoesNotExist:
                raise serializers.ValidationError("Product not found")
        
        return data
