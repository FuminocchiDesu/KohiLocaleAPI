from django.contrib import admin
from .models import User, CoffeeShop, BasicUser, CoffeeShopOwner, Rating
# Register your models here.
admin.site.register(User)
admin.site.register(CoffeeShop)
admin.site.register(BasicUser)
admin.site.register(CoffeeShopOwner)
admin.site.register(Rating)