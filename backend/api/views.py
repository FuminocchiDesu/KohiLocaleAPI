# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import User, CoffeeShop, BasicUser, CoffeeShopOwner, Rating
from .serializers import UserSerializer, CoffeeShopSerializer, BasicUserSerializer, CoffeeShopOwnerSerializer, RatingSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class CoffeeShopViewSet(viewsets.ModelViewSet):
    queryset = CoffeeShop.objects.all()
    serializer_class = CoffeeShopSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def rate(self, request, pk=None):
        coffee_shop = self.get_object()
        user = request.user
        stars = request.data.get('stars')
        description = request.data.get('description', '')

        rating, created = Rating.objects.update_or_create(
            user=user,
            coffee_shop=coffee_shop,
            defaults={'stars': stars, 'description': description}
        )

        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class BasicUserViewSet(viewsets.ModelViewSet):
    queryset = BasicUser.objects.all()
    serializer_class = BasicUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BasicUser.objects.filter(user=self.request.user)

class CoffeeShopOwnerViewSet(viewsets.ModelViewSet):
    queryset = CoffeeShopOwner.objects.all()
    serializer_class = CoffeeShopOwnerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CoffeeShopOwner.objects.filter(user=self.request.user)
