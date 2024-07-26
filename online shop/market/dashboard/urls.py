from django.urls import path
from .views import (
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    BrandListView, BrandCreateView, BrandUpdateView, BrandDeleteView,
    ProductListView, ProductCreateView, ProductUpdateView, ProductDeleteView,
    ProductImageCreateView, ProductImageUpdateView, ProductImageDeleteView, index
)

urlpatterns = [
    path('', index, name='dashboard'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category-delete'),
    path('brands/', BrandListView.as_view(), name='brand-list'),
    path('brands/create/', BrandCreateView.as_view(), name='brand-create'),
    path('brands/<int:pk>/update/', BrandUpdateView.as_view(), name='brand-update'),
    path('brands/<int:pk>/delete/', BrandDeleteView.as_view(), name='brand-delete'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/<int:product_id>/images/create/', ProductImageCreateView.as_view(), name='productimage-create'),
    path('products/images/<int:pk>/update/', ProductImageUpdateView.as_view(), name='productimage-update'),
    path('products/images/<int:pk>/delete/', ProductImageDeleteView.as_view(), name='productimage-delete'),
]
