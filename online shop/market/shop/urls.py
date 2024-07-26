from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    index, sort_by_brands,
    sort_by_category, product_detail
)

urlpatterns = [
    path('', index, name='shop'),
    path('sort_by_brands/<int:pk>', sort_by_brands, name="sort_by_brand"),
    path('sort_by_category/<int:pk>', sort_by_category, name="sort_by_category"),
    path('product/<int:pk>', product_detail, name='product_detail'),
]
