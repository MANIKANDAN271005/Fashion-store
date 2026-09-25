from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from accounts.models import CustomUser, Product, Cart, Order, Wishlist, Category, OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Count, F
from django.contrib import messages

SHIPPING_FEE = 150


class OutOfStock(Exception):
    """Raised inside checkout to roll back the order when a cart item exceeds stock."""

    def __init__(self, product):
        super().__init__(product.name)
        self.product = product

# Price filter buckets shown in the shop sidebar: key -> (label, min, max)
PRICE_RANGES = {
    "under-1000": ("Under ₹1,000", None, 1000),
    "1000-2000": ("₹1,000 – ₹1,999", 1000, 2000),
    "2000-4000": ("₹2,000 – ₹3,999", 2000, 4000),
    "4000-plus": ("₹4,000 & above", 4000, None),
}

SORT_OPTIONS = {
    "newest": ("Newest", "-created_at"),
    "price-asc": ("Price: Low to High", "price"),
    "price-desc": ("Price: High to Low", "-price"),
    "name": ("Name: A to Z", "name"),
}


def search_products(products, query):
    """Every word in the query must match the name, description or category."""
    for term in query.split():
        products = products.filter(
            Q(name__icontains=term) |
            Q(description__icontains=term) |
            Q(category__name__icontains=term)
        )
    return products


def filter_products(request, products):
    """Apply the ?category=, ?price= and ?sort= filters shared by the shop pages."""

    category = request.GET.get("category", "").strip()
    price = request.GET.get("price", "")
    sort = request.GET.get("sort", "newest")

    if category:
        products = products.filter(category__name__iexact=category)

    if price in PRICE_RANGES:
        _, low, high = PRICE_RANGES[price]
        if low is not None:
            products = products.filter(price__gte=low)
        if high is not None:
            products = products.filter(price__lt=high)
    else:
        price = ""

    if sort not in SORT_OPTIONS:
        sort = "newest"
    products = products.order_by(SORT_OPTIONS[sort][1], "-id")

    return products, {
        "selected_category": category,
        "selected_price": price,
        "selected_price_label": PRICE_RANGES[price][0] if price else "",
        "selected_sort": sort,
        "price_ranges": [(key, value[0]) for key, value in PRICE_RANGES.items()],
        "sort_options": [(key, value[0]) for key, value in SORT_OPTIONS.items()],
        "categories": Category.objects.annotate(
            product_count=Count("product", filter=Q(product__is_available=True))
        ).order_by("name"),
    }


def home(request):

    products = Product.objects.filter(is_available=True).select_related("category").order_by("-created_at", "-id")

    return render(
        request,
        'home.html',
        {
            'products': products[:8],
        }
    )

def shop(request):

    products = Product.objects.filter(is_available=True).select_related("category")

    products, context = filter_products(request, products)

    context.update({
        "products": products,
        "is_filtered": bool(context["selected_category"] or context["selected_price"]),
    })

    return render(request, "shop.html", context)

def about(request):
    return render(request,'about.html')

CATEGORY_DISPLAY_IMAGES = {
    "men": "images/men4.jpg",
    "women": "images/women5.jpg",
    "kids": "images/kids3.png",
    "shoes": "images/shoes5.jpg",
    "footwear": "images/shoes5.jpg",
    "accessories": "images/Accessories1.jpg",
    "watches": "images/watches3.jpg",
}
DEFAULT_CATEGORY_IMAGE = "images/productimage11.jpg"

def collections(request):

    categories = list(Category.objects.all())

    for cat in categories:
        cat.display_image = CATEGORY_DISPLAY_IMAGES.get(
            cat.name.strip().lower(), DEFAULT_CATEGORY_IMAGE
        )

    products = Product.objects.filter(is_available=True).select_related("category").order_by("-created_at", "-id")

    category_id = request.GET.get('category', '')
    selected = None

    if category_id.isdigit():
        selected = next((cat for cat in categories if cat.id == int(category_id)), None)
        products = products.filter(category_id=category_id)

    return render(request, "collections.html", {
        "products": products,
        "categories": categories,
        "selected_category": selected,
    })

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not message:
            messages.error(request, "Please fill in all required fields.")
        else:
            messages.success(request, "Thank you! Your message has been sent.")
            return redirect("contact")

    return render(request, 'contact.html')


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return render(request, "login.html")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")

        if not user.is_active:
            messages.error(request, "This account is inactive.")
            return render(request, "login.html")

        login(request, user)

        if user.is_superuser:
            return redirect("admin_dashboard")

        elif user.role == "seller":
            return redirect("seller_dashboard")

        return redirect("dashboard")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):

    if request.method == "POST":

        fullname = request.POST.get("fullname", "").strip()
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        password1 = request.POST.get("password1", "")
        password2 = request.POST.get("password2", "")
        role = request.POST.get("role")

        if not fullname or not username or not email or not role:
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        if len(password1) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect("register")

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

    products = Product.objects.filter(is_available=True).select_related("category")

    products, context = filter_products(request, products)

    context["products"] = products

    return render(request, "category.html", context)

def search(request):

    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_available=True).select_related("category")

    if query:
        products = search_products(products, query)

    products, context = filter_products(request, products)

    context.update({
        "products": products if query else products.none(),
        "query": query,
    })

    return render(request, "search.html", context)

@login_required
def checkout(request):

    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items and request.method == "GET":
        messages.error(request, "Your cart is empty.")
        return redirect("cart")

    subtotal = sum(
        item.product.price * item.quantity
        for item in cart_items
    )

    total = subtotal + SHIPPING_FEE

    context = {
        "subtotal": subtotal,
        "shipping_fee": SHIPPING_FEE,
        "total": total,
        "cart_items": cart_items,
    }

    if request.method == "POST":

        if not cart_items:
            messages.error(request, "Your cart is empty.")
            return redirect("cart")

        details = {
            field: request.POST.get(field, "").strip()
            for field in ("full_name", "phone", "address", "city", "state", "pincode")
        }
        payment = request.POST.get("payment", "")

        if not all(details.values()):
            messages.error(request, "Please complete all delivery details.")
            return render(request, "checkout.html", context)

        if payment not in dict(Order.PAYMENT_CHOICES):
            messages.error(request, "Please choose a valid payment method.")
            return render(request, "checkout.html", context)

        try:
            with transaction.atomic():

                order = Order.objects.create(
                    user=request.user,
                    payment_method=payment,
                    total_price=total,
                    **details,
                )

                for item in cart_items:

                    product = item.product

                    # Conditional update so two shoppers can't buy the same last unit.
                    reserved = Product.objects.filter(
                        id=product.id,
                        is_available=True,
                        stock__gte=item.quantity,
                    ).update(stock=F("stock") - item.quantity)

                    if not reserved:
                        raise OutOfStock(product)

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item.quantity,
                        price=product.price
                    )

                cart_items.delete()

        except OutOfStock as error:
            product = Product.objects.get(id=error.product.id)
            if not product.is_available or product.stock == 0:
                messages.error(request, f"\"{product.name}\" is no longer available. Please remove it from your cart.")
            else:
                messages.error(request, f"Only {product.stock} of \"{product.name}\" left in stock. Please update your cart.")
            return redirect("cart")

        return redirect("order_success")

    return render(request, "checkout.html", context)

@login_required
def order_detail(request, id):

    if request.user.is_superuser:
        order = get_object_or_404(Order, id=id)
    else:
        order = get_object_or_404(Order, id=id, user=request.user)

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

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
    ).exclude(
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
    product = get_object_or_404(Product, id=id)

    if not product.is_available or product.stock <= 0:
        messages.error(request, "This product is currently unavailable.")
        return redirect('product_detail', id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        if cart_item.quantity >= product.stock:
            messages.error(request, f"Only {product.stock} of \"{product.name}\" in stock.")
        else:
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

@login_required
def cart(request):

    cart_items = Cart.objects.filter(user=request.user)

    subtotal = 0

    for item in cart_items:

        subtotal += item.product.price * item.quantity

    shipping = SHIPPING_FEE if cart_items else 0

    return render(
        request,
        "cart.html",
        {
            "cart_items": cart_items,
            "subtotal": subtotal,
            "shipping": shipping,
            "grand_total": subtotal + shipping,
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

    if cart_item.quantity >= cart_item.product.stock:
        messages.error(request, f"Only {cart_item.product.stock} of \"{cart_item.product.name}\" in stock.")
    else:
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

    if not product.is_available or product.stock <= 0:
        messages.error(request, "This product is currently unavailable.")
        return redirect('product_detail', id=id)

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