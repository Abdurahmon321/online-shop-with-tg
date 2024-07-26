from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from PIL import Image
import numpy as np
import io
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.paginator import Paginator
from skimage.metrics import structural_similarity as ssim

from shop.models import (
    Category, Brand, Product, ProductImage, ProductVideo, Cart, CartProduct,
    UserProfile, Comment, LikeProduct, Dislike, ViewProduct, DiscountProduct
)
from shop.serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, ProductImageSerializer,
    ProductVideoSerializer, CartSerializer, CartProductSerializer, UserSerializer,
    UserProfileSerializer, CommentSerializer, LikeProductSerializer, DislikeSerializer,
    ViewProductSerializer, DiscountProductSerializer
)

from .serializers import ProductSerializer, ProductImageSerializer, CategorySerializer, BrandSerializer

# Create your views here.
class ProductSearchView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )


class RegisterView(APIView):
    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    @action(detail=False, methods=['get'], url_path='parent-categories')
    def get_parent_categories(self, request):
        categories = Category.objects.filter(parent__isnull=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='subcategories')
    def get_subcategories(self, request, pk=None):
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = self.get_serializer(subcategories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='edit')
    def edit_category(self, request, pk=None):
        category = self.get_object()
        serializer = self.get_serializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_category(self, request, pk=None):
        category = self.get_object()
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['patch'], url_path='edit')
    def edit_product(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_product(self, request, pk=None):
        product = self.get_object()
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    @action(detail=False, methods=['post'], url_path='compare')
    def compare_image(self, request):
        if request.method == 'POST' and request.FILES.get('image'):
            uploaded_image = request.FILES['image']
            uploaded_image = Image.open(uploaded_image).convert('L').resize(
                (200, 200))  # Convert to grayscale and resize
            uploaded_array = np.array(uploaded_image)

            for product_image in ProductImage.objects.all():
                product_image_file = Image.open(product_image.image.path).convert('L').resize(
                    (200, 200))  # Convert to grayscale and resize
                product_image_array = np.array(product_image_file)

                # Calculate SSIM
                similarity, _ = ssim(uploaded_array, product_image_array, full=True)
                if similarity > 0.8:
                    product = product_image.product
                    product_data = {
                        'name': product.name,
                        'product_price': str(product.price),
                        'product_category': product.category.name,
                        'product_brand': product.brand.name,
                        'description': product.description,
                        'images': [request.build_absolute_uri(image.image.url) for image in product.images.all()]
                    }
                    return JsonResponse(product_data)

            return JsonResponse({'error': 'No matching product found'}, status=404)
        return JsonResponse({'error': 'Invalid request'}, status=400)


class ProductVideoViewSet(viewsets.ModelViewSet):
    queryset = ProductVideo.objects.all()
    serializer_class = ProductVideoSerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartProductViewSet(viewsets.ModelViewSet):
    queryset = CartProduct.objects.all()
    serializer_class = CartProductSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class LikeProductViewSet(viewsets.ModelViewSet):
    queryset = LikeProduct.objects.all()
    serializer_class = LikeProductSerializer


class DislikeViewSet(viewsets.ModelViewSet):
    queryset = Dislike.objects.all()
    serializer_class = DislikeSerializer


class ViewProductViewSet(viewsets.ModelViewSet):
    queryset = ViewProduct.objects.all()
    serializer_class = ViewProductSerializer


class DiscountProductViewSet(viewsets.ModelViewSet):
    queryset = DiscountProduct.objects.all()
    serializer_class = DiscountProductSerializer