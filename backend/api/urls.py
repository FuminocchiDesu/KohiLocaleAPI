# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, CoffeeShopViewSet, BasicUserViewSet, CoffeeShopOwnerViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'coffee-shops', CoffeeShopViewSet)
router.register(r'basic-users', BasicUserViewSet)
router.register(r'coffee-shop-owners', CoffeeShopOwnerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]