from rest_framework import serializers

from .models import (User,
                     Banner,
                     Category,
                     Product,
                     OrderItem,
                     Order)


class CatalogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id',
                  'name_en',
                  'name_hu')


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ('image',
                  'name_en',
                  'name_hu')


class ProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id',
                  'name_en',
                  'name_en',
                  'thumbnail',
                  'is_best',
                  'price',
                  'discount',
                  'new_price')

    def to_representation(self, instance):
        if not instance.is_active:
            return None
        return super().to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username',
                  'phone_number']


class CatalogueWithImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id',
                  'name_en',
                  'name_hu',
                  'image')





class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ('id',
                  'name_en',
                  'name_hu',
                  'description_en',
                  'description_hu',
                  'image',
                  'is_best',
                  'price',
                  'discount',
                  'new_price')

    def to_representation(self, instance):

        if not instance.is_active:
            return None
        
        return super().to_representation(instance)


class MenuSerializer(serializers.ModelSerializer):

    products = ProductItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('id',
                  'name_en',
                  'name_hu',
                  'products')


class MenuWithoutIdSerializer(serializers.ModelSerializer):

    products = ProductItemSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('name_en',
                  'name_hu',
                  'image',
                  'products')


class OrderItemSerializer(serializers.ModelSerializer):

    product = ProductItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id',
                  'quantity',
                  'total',
                  'product',)


class OrderSerializer(serializers.ModelSerializer):

    orders = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('id', 'sum_total', 'orders')
