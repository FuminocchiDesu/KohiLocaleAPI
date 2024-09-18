# serializers.py
from rest_framework import serializers
from .models import User, CoffeeShop, BasicUser, CoffeeShopOwner, Rating

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'contact_number', 'bio', 'profile_picture', 'is_owner')
        extra_kwargs = {'password': {'write_only': True}}

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