# serializers.py
from rest_framework import serializers
from .models import User, CoffeeShop, BasicUser, CoffeeShopOwner, Rating, CoffeeShopApplication, MenuCategory, MenuItem, Promo, BugReport
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        login = data.get('login')
        password = data.get('password')

        if login and password:
            # Try to authenticate with username
            user = authenticate(username=login, password=password)
            
            # If authentication fails, try with email
            if user is None:
                try:
                    user_obj = User.objects.get(email=login)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "login" and "password".')

        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'contact_number', 'bio', 'profile_picture', 'is_owner')
        extra_kwargs = {'password': {'write_only': True}}
   
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
class CoffeeShopSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = CoffeeShop
        fields = ('id', 'name', 'address', 'description', 'opening_hours', 'image', 'owner', 'average_rating')

class BasicUserSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    favorite_coffee_shop = CoffeeShopSerializer(read_only=True)
    favorite_coffee_shop_id = serializers.PrimaryKeyRelatedField(
        queryset=CoffeeShop.objects.all(),
        source='favorite_coffee_shop',
        write_only=True,
        allow_null=True
    )

    class Meta:
        model = BasicUser
        fields = ('id', 'user', 'favorite_coffee_shop', 'favorite_coffee_shop_id')

class CoffeeShopOwnerSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    owned_coffee_shops = CoffeeShopSerializer(many=True, read_only=True)

    class Meta:
        model = CoffeeShopOwner
        fields = ('id', 'user', 'owned_coffee_shops')

class RatingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ('id', 'user', 'coffee_shop', 'stars', 'description', 'created_at')

class CoffeeShopApplicationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = CoffeeShopApplication
        fields = ['id', 'user', 'name', 'address', 'description', 'opening_hours', 'image', 'status']
        read_only_fields = ['user', 'status']

class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = ['id', 'name', 'coffee_shop']
        read_only_fields = ['coffee_shop']

class MenuItemSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'category', 'image']
        read_only_fields = ['category']

class PromoSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = Promo
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'coffee_shop', 'image']
        read_only_fields = ['coffee_shop']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Rating
        fields = ['id', 'user', 'coffee_shop', 'stars', 'description', 'created_at']
        read_only_fields = ['user', 'coffee_shop']

class BugReportSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BugReport
        fields = ['id', 'user', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['user', 'status', 'created_at', 'updated_at']