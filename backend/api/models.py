# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from django.conf import settings

class User(AbstractUser):
    contact_number = models.CharField(max_length=20, blank=True, default='')
    bio = models.TextField(blank=True, default='')
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.png')
    is_owner = models.BooleanField(default=False)

    def get_profile_picture_url(self):
        if self.profile_picture:
            return f"{settings.MEDIA_URL}{self.profile_picture}"
        return f"{settings.MEDIA_URL}profile_pictures/default.png"

class CoffeeShop(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    description = models.TextField()
    opening_hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to='coffee_shop_images/', blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_coffee_shops')

    def __str__(self):
        return self.name

    def average_rating(self):
        return self.ratings.aggregate(Avg('stars'))['stars__avg'] or 0

class BasicUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='basic_user')
    favorite_coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.SET_NULL, null=True, blank=True)

class CoffeeShopOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coffee_shop_owner')

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE, related_name='ratings')
    stars = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'coffee_shop')

    def __str__(self):
        return f"{self.user.username}'s {self.stars}-star rating for {self.coffee_shop.name}"
    
class CoffeeShopApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    description = models.TextField()
    opening_hours = models.CharField(max_length=100)
    image = models.ImageField(upload_to='coffee_shop_application_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
class MenuCategory(models.Model):
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE, related_name='menu_categories')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.coffee_shop.name} - {self.name}"

class MenuItem(models.Model):
    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_item_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.category.coffee_shop.name} - {self.category.name} - {self.name}"

class Promo(models.Model):
    coffee_shop = models.ForeignKey(CoffeeShop, on_delete=models.CASCADE, related_name='promos')
    name = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='promo_images/', blank=True, null=True)

    def __str__(self):
        return f"{self.coffee_shop.name} - {self.name}"
    
class BugReport(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_process', 'In Process'),
        ('fixed', 'Fixed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Bug Report by {self.user.username} - {self.status}"
    

