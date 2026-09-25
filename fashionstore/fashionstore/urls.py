from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views, admin_views

urlpatterns = [

    # Home
    path('', views.home, name='home'),
    path("shop/", views.shop, name="shop"),

    # Pages
    path('about/', views.about, name='about'),
    path('collections/', views.collections, name='collections'),
    path('contact/', views.contact, name='contact'),
    path('category/', views.category, name='category'),
    path("search/", views.search, name="search"),

    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # Product
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('add-product/', views.add_product, name='add_product'),

    # Cart
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-cart/<int:id>/', views.remove_cart, name='remove_cart'),
    path('increase-cart/<int:id>/', views.increase_cart, name='increase_cart'),
    path('decrease-cart/<int:id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-cart-item/<int:id>/',views.remove_cart_item,name='remove_cart_item'),

    # Wishlist
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/',views.add_to_wishlist,name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/',views.remove_from_wishlist,name='remove_from_wishlist'),

    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),
    path('order/<int:id>/', views.order_detail, name='order_detail'),
    path("order-success/", views.order_success, name="order_success"),

    # Dashboards
    path('dashboard/', views.dashboard, name='dashboard'),
    path('seller-dashboard/', views.seller_dashboard, name='seller_dashboard'),

    # Custom Admin Panel (superuser only)
    path('admin-dashboard/', admin_views.dashboard, name='admin_dashboard'),
    path('admin-dashboard/products/', admin_views.product_list, name='admin_products'),
    path('admin-dashboard/products/add/', admin_views.product_add, name='admin_product_add'),
    path('admin-dashboard/products/<int:id>/edit/', admin_views.product_edit, name='admin_product_edit'),
    path('admin-dashboard/products/<int:id>/delete/', admin_views.product_delete, name='admin_product_delete'),
    path('admin-dashboard/products/<int:id>/toggle/', admin_views.product_toggle_availability, name='admin_product_toggle'),
    path('admin-dashboard/products/<int:id>/stock/', admin_views.product_update_stock, name='admin_product_stock'),
    path('admin-dashboard/categories/', admin_views.category_list, name='admin_categories'),
    path('admin-dashboard/categories/add/', admin_views.category_add, name='admin_category_add'),
    path('admin-dashboard/categories/<int:id>/edit/', admin_views.category_edit, name='admin_category_edit'),
    path('admin-dashboard/categories/<int:id>/delete/', admin_views.category_delete, name='admin_category_delete'),

    # Django Admin
    path('admin/', admin.site.urls),

    path("buy/<int:id>/", views.buy_now, name="buy_now"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)