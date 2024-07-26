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

from .models import (
    Category, Brand, Product, ProductImage, ProductVideo, Cart, CartProduct,
    UserProfile, Comment, LikeProduct, Dislike, ViewProduct, DiscountProduct
)
from .serializers import (
    CategorySerializer, BrandSerializer, ProductSerializer, ProductImageSerializer,
    ProductVideoSerializer, CartSerializer, CartProductSerializer, UserSerializer,
    UserProfileSerializer, CommentSerializer, LikeProductSerializer, DislikeSerializer,
    ViewProductSerializer, DiscountProductSerializer
)


def index(request):
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000000)
    product_list = Product.objects.filter(price__gte=min_price, price__lte=max_price, available=True)
    sort_by = request.GET.get('sort_by', 'most_viewed')

    if sort_by == 'newest':
        product_list = product_list.order_by('-created_at')
    elif sort_by == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_by == 'price_asc':
        product_list = product_list.order_by('price')
    else:  # highest_rated
        product_list = product_list.order_by('-views')

    product_count = product_list.count()
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/shop.html', {'page_obj': page_obj, "product_count": product_count,
                                              'min_price': min_price, 'max_price': max_price})


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


def sort_by_brands(request, pk):
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000000)
    product_list = Product.objects.filter(brand_id=pk, price__gte=min_price, price__lte=max_price)
    sort_by = request.GET.get('sort_by', 'most_viewed')

    if sort_by == 'newest':
        product_list = product_list.order_by('-created_at')
    elif sort_by == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_by == 'price_asc':
        product_list = product_list.order_by('price')
    else:  # highest_rated
        product_list = product_list.order_by('-views')


    product_count = product_list.count()
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)



    return render(request, 'shop/shop.html', {'page_obj': page_obj, "product_count": product_count,
                                              'min_price': min_price, 'max_price': max_price})


def sort_by_category(request, pk):
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 1000000)
    product_list = Product.objects.filter(category_id=pk, price__gte=min_price, price__lte=max_price)
    sort_by = request.GET.get('sort_by', 'most_viewed')

    if sort_by == 'newest':
        product_list = product_list.order_by('-created_at')
    elif sort_by == 'price_desc':
        product_list = product_list.order_by('-price')
    elif sort_by == 'price_asc':
        product_list = product_list.order_by('price')
    else:  # highest_rated
        product_list = product_list.order_by('-views')

    product_count = product_list.count()
    paginator = Paginator(product_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shop/shop.html', {'page_obj': page_obj, "product_count": product_count,
                                              'min_price': min_price, 'max_price': max_price})





