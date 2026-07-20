from django.contrib import admin
from .models import CustomUser, Category, Product, Cart, Order, Wishlist
from .models import OrderItem

admin.site.register(CustomUser)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Wishlist)

admin.site.site_header = "Fashion Store Admin"
admin.site.site_title = "Dashboard"
admin.site.index_title = "Management Panel"
