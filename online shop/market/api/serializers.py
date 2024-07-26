from rest_framework import serializers
from shop.models import Product, Category, Brand, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description']
        ref_name = 'Api_Brand'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'product']


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    brand = serializers.PrimaryKeyRelatedField(queryset=Brand.objects.all())
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'brand', 'stock', 'images', 'available', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        # remove category and brand data from validated_data
        category = validated_data.pop('category', None)
        brand = validated_data.pop('brand', None)

        # Update the instance with remaining validated data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update category and brand if provided
        if category:
            instance.category = category
        if brand:
            instance.brand = brand

        instance.save()
        return instance
