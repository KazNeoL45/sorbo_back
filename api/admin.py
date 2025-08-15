from django.contrib import admin
from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'type', 'price_cents', 'currency', 'stock', 'created_at']
    list_filter = ['type', 'currency', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'buyer_full_name', 'product', 'status', 'total_cents', 'currency', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['buyer_full_name', 'buyer_address', 'stripe_session_id']
    readonly_fields = ['id', 'stripe_session_id', 'created_at', 'updated_at']
    ordering = ['-created_at']
