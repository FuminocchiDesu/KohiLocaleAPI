# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, UserViewSet, CoffeeShopViewSet, BasicUserViewSet, CoffeeShopOwnerViewSet, CoffeeShopApplicationViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'users', UserViewSet)
router.register(r'coffee-shops', CoffeeShopViewSet)
router.register(r'basic-users', BasicUserViewSet)
router.register(r'coffee-shop-owners', CoffeeShopOwnerViewSet)
router.register(r'coffee-shop-applications', CoffeeShopApplicationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]