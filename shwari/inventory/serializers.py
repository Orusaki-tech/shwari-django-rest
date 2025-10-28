from rest_framework import serializers
from .models import Product, Order, OrderItem, Customer, Review, ProductAccessory,Admin, Color, User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('product_name', 'product_type', 'product_description', 'product_price', 'product_quantity', 'product_sku', 'product_color', 'product_image_url', 'related_accessories')


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ''      

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'  

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'  

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ProductAccessorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAccessory
        fields = '__all__'  


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'      



class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'      





