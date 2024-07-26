from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, BrandViewSet, ProductViewSet, ProductImageViewSet,
    ProductVideoViewSet, CartViewSet, CartProductViewSet, UserViewSet,
    UserProfileViewSet, RegisterView, CommentViewSet, ProductSearchView,
    LikeProductViewSet, DislikeViewSet, ViewProductViewSet, DiscountProductViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'brands', BrandViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'product-videos', ProductVideoViewSet)
router.register(r'carts', CartViewSet)
router.register(r'cart-products', CartProductViewSet)
router.register(r'users', UserViewSet)
router.register(r'user-profiles', UserProfileViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'like-products', LikeProductViewSet)
router.register(r'dislikes', DislikeViewSet)
router.register(r'view-products', ViewProductViewSet)
router.register(r'discount-products', DiscountProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('search/', ProductSearchView.as_view(), name='product-search'),
    path('auth', include('rest_framework.urls')),
    path('register/', RegisterView.as_view(), name='register'),
]
