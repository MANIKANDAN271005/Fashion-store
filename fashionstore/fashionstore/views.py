from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser, Product, Cart, Order, Wishlist, Category, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.contrib import messages

def home(request):

    products = Product.objects.all()

    category = request.GET.get('category')

    if category:
        products = products.filter(
            category__name=category
        )

    return render(
        request,
        'home.html',
        {
            'products': products
        }
    )

def shop(request):

    products = Product.objects.all()

    category = request.GET.get("category")

    if category:
        products = products.filter(category__name=category)

    return render(
        request,
        "shop.html",
        {
            "products": products
        }
    )

def about(request):
    return render(request,'about.html')

def collections(request):

    categories = Category.objects.all()

    products = Product.objects.all()

    category_id = request.GET.get('category')

    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, "collections.html", {
        "products": products,
        "categories": categories
    })

def contact(request):
    return render(request,'contact.html')


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username").strip()
        password = request.POST.get("password")
        role = request.POST.get("role")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(request, "Invalid Username or Password")
            return render(request, "login.html")

        if not user.is_active:
            messages.error(request, "Account is inactive")
            return render(request, "login.html")

        # Check selected role
        if role == "seller" and user.role != "seller":
            messages.error(request, "This is not a Seller account.")
            return render(request, "login.html")

        if role == "user" and user.role != "user":
            messages.error(request, "This is not a User account.")
            return render(request, "login.html")

        if role == "admin" and not user.is_superuser:
            messages.error(request, "This is not an Admin account.")
            return render(request, "login.html")

        login(request, user)

        if user.is_superuser:
            return redirect("admin_dashboard")

        elif user.role == "seller":
            return redirect("seller_dashboard")

        return redirect("user_dashboard")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        role = request.POST.get("role")

        if password1 != password2:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        user.first_name = fullname
        user.phone = phone
        user.role = role

        user.save()

        messages.success(request, "Registration Successful")

        return redirect("login")

    return render(request, "register.html")

def category(request):

    categories = Category.objects.all()

    return render(request, "category.html", {
        "categories": categories
    })

def search(request):

    query = request.GET.get("q", "")

    products = Product.objects.all()

    if query:

        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    return render(
        request,
        "shop.html",
        {
            "products": products,
            "query": query
        }
    )

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    total = subtotal + 150

    if request.method == "POST":

        order = Order.objects.create(
            user=request.user,
            full_name=request.POST["full_name"],
            phone=request.POST["phone"],
            address=request.POST["address"],
            city=request.POST["city"],
            state=request.POST["state"],
            pincode=request.POST["pincode"],
            payment_method=request.POST["payment"],
            total_price=total)

        for item in cart_items:

            OrderItem.objects.create(
    order=order,
    product=item.product,
    quantity=item.quantity,
    price=item.product.price
)

        cart_items.delete()

        return redirect("order_success")

    return render(
        request,
        "checkout.html",
        {
            "subtotal": subtotal,
            "total": total
        }
    )

def order_detail(request, id):

    order = get_object_or_404(Order, id=id)

    # Replace this with your actual OrderItem model if you have one
    items = OrderItem.objects.filter(order=order)

    return render(request, "order_detail.html", {
        "order": order,
        "items": items,
    })

def order_success(request):

    return render(
        request,
        "order_success.html"
    )

def product_detail(request, id):

    product = get_object_or_404(Product, id=id)

    related_products = Product.objects.exclude(
        id=id
    )[:4]

    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def add_to_cart(request, id):
    product = Product.objects.get(id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def remove_cart(request, id):
    item = Cart.objects.get(id=id)

    if item.user == request.user:
        item.delete()

    return redirect('cart')

@login_required
def user_dashboard(request):

    orders = Order.objects.filter(
        user=request.user
    )

    context = {
        'orders': orders,
        'total_orders': orders.count(),
        'total_cart': Cart.objects.filter(
            user=request.user
        ).count(),
        'total_wishlist': Wishlist.objects.filter(
            user=request.user
        ).count()
    }

    return render(
        request,
        'user_dashboard.html',
        context
    )

@login_required
def seller_dashboard(request):

    if request.user.role != "seller":
        return redirect("home")

    products = Product.objects.filter(
        seller=request.user
    )

    return render(
        request,
        "seller_dashboard.html",
        {
            "products": products,
            "total_products": products.count()
        }
    )

@login_required
def admin_dashboard(request):

    users = User.objects.count()

    products = Product.objects.count()

    orders = Order.objects.count()

    revenue = sum(order.total_price for order in Order.objects.all())

    recent_orders = Order.objects.order_by('-id')[:10]

    return render(request, "admin_dashboard.html", {
        "users": users,
        "products": products,
        "orders": orders,
        "revenue": revenue,
        "recent_orders": recent_orders,
    })
@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    return render(
        request,
        "wishlist.html",
        {
            "wishlist_items": wishlist_items
        }
    )

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect("wishlist")

@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).delete()

    return redirect("wishlist")

def category_products(request, id):
    products = Product.objects.filter(
        category=id
    )

    return render(
        request,
        'shop.html',
        {'products': products}
    )

@login_required
def cart(request):

    cart_items = Cart.objects.filter(user=request.user)

    total = 0

    for item in cart_items:

        total += item.product.price * item.quantity

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "total": total,
        },
    )

@login_required
def dashboard(request):

    recent_orders = Order.objects.filter(
        user=request.user
    ).order_by("-id")[:5]

    cart_count = Cart.objects.filter(
        user=request.user
    ).count()

    order_count = Order.objects.filter(
        user=request.user
    ).count()

    wishlist_count = Wishlist.objects.filter(user=request.user).count()

    return render(
    request,
    "dashboard.html",
    {
        "recent_orders": recent_orders,
        "orders": order_count,
        "wishlist": wishlist_count,
        "cart": cart_count,
    }
)

User = get_user_model()

@login_required
def increase_cart(request, id):

    cart_item = get_object_or_404(
        Cart,
        id=id,
        user=request.user
    )

    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")

@login_required
def decrease_cart(request, id):

    cart_item = get_object_or_404(
        Cart,
        id=id,
        user=request.user
    )

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    else:
        cart_item.delete()

    return redirect("cart")

@login_required
def remove_cart_item(request, id):

    cart_item = get_object_or_404(
        Cart,
        id=id,
        user=request.user
    )

    cart_item.delete()

    return redirect("cart")

@login_required
def buy_now(request, id):

    product = get_object_or_404(Product, id=id)

    cart, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart.quantity = 1
        cart.save()

    return redirect("checkout")

@login_required
def add_product(request):

    # Only sellers can add products
    if request.user.role != "seller":
        messages.error(request, "Only sellers can add products.")
        return redirect("home")

    categories = Category.objects.all()

    if request.method == "POST":

        Product.objects.create(
            seller=request.user,
            category=Category.objects.get(id=request.POST["category"]),
            name=request.POST["name"],
            description=request.POST["description"],
            price=request.POST["price"],
            stock=request.POST["stock"],
            image=request.FILES.get("image")
        )

        messages.success(request, "Product Added Successfully.")
        return redirect("seller_dashboard")

    return render(
        request,
        "add_product.html",
        {
            "categories": categories
        }
    )

@login_required
def orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by("-ordered_at")

    return render(
        request,
        "orders.html",
        {
            "orders": orders
        }
    )