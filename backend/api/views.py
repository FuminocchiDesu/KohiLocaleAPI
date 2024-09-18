# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from .models import User, CoffeeShop, BasicUser, CoffeeShopOwner, Rating, MenuItem, MenuCategory, CoffeeShopApplication, Promo, BugReport
from .serializers import (UserSerializer, CoffeeShopSerializer, BasicUserSerializer, CoffeeShopOwnerSerializer, RatingSerializer, 
                          UserLoginSerializer, UserRegistrationSerializer, MenuCategorySerializer, MenuItemSerializer, BugReportSerializer, 
                          PromoSerializer, CoffeeShopApplicationSerializer)

class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['POST'])
    def register(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        })

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

class MenuCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = MenuCategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return MenuCategory.objects.filter(coffee_shop_id=self.kwargs['coffee_shop_pk'])

    def perform_create(self, serializer):
        coffee_shop = get_object_or_404(CoffeeShop, pk=self.kwargs['coffee_shop_pk'])
        serializer.save(coffee_shop=coffee_shop)

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return MenuItem.objects.filter(category__coffee_shop_id=self.kwargs['coffee_shop_pk'])

    def perform_create(self, serializer):
        category = get_object_or_404(MenuCategory, pk=self.kwargs['category_pk'], coffee_shop_id=self.kwargs['coffee_shop_pk'])
        serializer.save(category=category)

class PromoViewSet(viewsets.ModelViewSet):
    serializer_class = PromoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Promo.objects.filter(coffee_shop_id=self.kwargs['coffee_shop_pk'])

    def perform_create(self, serializer):
        coffee_shop = get_object_or_404(CoffeeShop, pk=self.kwargs['coffee_shop_pk'])
        serializer.save(coffee_shop=coffee_shop)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Rating.objects.filter(coffee_shop_id=self.kwargs['coffee_shop_pk'])

    def perform_create(self, serializer):
        coffee_shop = get_object_or_404(CoffeeShop, pk=self.kwargs['coffee_shop_pk'])
        serializer.save(user=self.request.user, coffee_shop=coffee_shop)

class BugReportViewSet(viewsets.ModelViewSet):
    queryset = BugReport.objects.all()
    serializer_class = BugReportSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def update_status(self, request, pk=None):
        bug_report = self.get_object()
        status = request.data.get('status')
        if status not in dict(BugReport.STATUS_CHOICES):
            return Response({'status': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        bug_report.status = status
        bug_report.save()
        return Response({'status': 'Bug report status updated'})
    
class CoffeeShopApplicationViewSet(viewsets.ModelViewSet):
    queryset = CoffeeShopApplication.objects.all()
    serializer_class = CoffeeShopApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return CoffeeShopApplication.objects.all()
        return CoffeeShopApplication.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def process_application(self, request, pk=None):
        application = self.get_object()
        action = request.data.get('action')
        
        if action not in ['approve', 'reject']:
            return Response({'error': 'Invalid action. Use "approve" or "reject".'}, status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'approve':
            # Create a new CoffeeShop instance
            CoffeeShop.objects.create(
                name=application.name,
                address=application.address,
                description=application.description,
                opening_hours=application.opening_hours,
                image=application.image,
                owner=application.user
            )
            application.status = 'approved'
            application.user.is_owner = True
            application.user.save()
        else:
            application.status = 'rejected'
        
        application.save()
        return Response({'status': f'Application {action}d'}, status=status.HTTP_200_OK)
