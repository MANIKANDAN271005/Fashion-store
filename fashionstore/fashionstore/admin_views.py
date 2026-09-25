from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count, Sum
from django.utils.http import url_has_allowed_host_and_scheme

from accounts.forms import ProductForm, form_error_messages
from accounts.models import Product, Category, Order, OrderItem

User = get_user_model()

LOW_STOCK_THRESHOLD = 5

# Product list status filter: key -> (label, queryset filter)
PRODUCT_STATUS_FILTERS = {
    'available': ('Available', Q(is_available=True, stock__gt=0)),
    'unavailable': ('Hidden (unavailable)', Q(is_available=False)),
    'out-of-stock': ('Out of stock', Q(stock=0)),
    'low-stock': (f'Low stock (1–{LOW_STOCK_THRESHOLD})', Q(stock__gt=0, stock__lte=LOW_STOCK_THRESHOLD)),
}


def _is_site_admin(user):
    return user.is_authenticated and user.is_superuser


admin_required = user_passes_test(_is_site_admin, login_url='login')


def _back_to_products(request):
    """Return to the (possibly filtered) product list the form was posted from."""
    next_url = request.POST.get('next', '')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect('admin_products')


@admin_required
def dashboard(request):

    revenue = Order.objects.aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'users': User.objects.count(),
        'products': Product.objects.count(),
        'categories': Category.objects.count(),
        'orders': Order.objects.count(),
        'revenue': revenue,
        'recent_orders': Order.objects.select_related('user').order_by('-id')[:10],
        'low_stock_products': Product.objects.select_related('category')
            .filter(stock__lte=LOW_STOCK_THRESHOLD).order_by('stock', 'name')[:10],
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    }

    return render(request, 'adminpanel/dashboard.html', context)


@admin_required
def product_list(request):

    products = Product.objects.select_related('category', 'seller').order_by('-created_at')

    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id.isdigit():
        products = products.filter(category_id=category_id)

    if status in PRODUCT_STATUS_FILTERS:
        products = products.filter(PRODUCT_STATUS_FILTERS[status][1])
    else:
        status = ''

    context = {
        'products': products,
        'categories': Category.objects.all(),
        'query': query,
        'selected_category': category_id,
        'selected_status': status,
        'status_filters': [(key, value[0]) for key, value in PRODUCT_STATUS_FILTERS.items()],
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    }

    return render(request, 'adminpanel/products.html', context)


def _product_form_context(request, product=None):
    return {
        'categories': Category.objects.all(),
        'product': product,
        'is_edit': product is not None,
        'form_data': request.POST if request.method == 'POST' else None,
    }


def _save_product_form(request, product=None):
    """Validate and save the add/edit form. Returns the saved product, or None if invalid."""

    form = ProductForm(request.POST, request.FILES, instance=product)

    if not form.is_valid():
        for error in form_error_messages(form):
            messages.error(request, error)
        return None

    saved = form.save(commit=False)
    if product is None:
        saved.seller = request.user
    saved.save()
    return saved


@admin_required
def product_add(request):

    if request.method == 'POST':
        product = _save_product_form(request)
        if product:
            messages.success(request, f'"{product.name}" was added successfully.')
            return redirect('admin_products')

    return render(request, 'adminpanel/product_form.html', _product_form_context(request))


@admin_required
def product_edit(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        # Validation mutates the instance, so keep the stored version for re-rendering on error.
        if _save_product_form(request, product):
            messages.success(request, f'"{product.name}" was updated successfully.')
            return redirect('admin_products')
        product.refresh_from_db()

    return render(request, 'adminpanel/product_form.html', _product_form_context(request, product))


@admin_required
def product_delete(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        # Order items cascade on product delete, so deleting would erase customers' order history.
        if OrderItem.objects.filter(product=product).exists():
            messages.error(
                request,
                f'"{product.name}" appears in past orders and cannot be deleted. '
                'Mark it unavailable instead to hide it from the store.'
            )
        else:
            name = product.name
            product.delete()
            messages.success(request, f'"{name}" was deleted.')

    return redirect('admin_products')


@admin_required
def product_update_stock(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        stock = request.POST.get('stock', '').strip()

        if not stock.isdigit():
            messages.error(request, 'Stock must be a whole number (0 or more).')
        else:
            product.stock = int(stock)
            product.save(update_fields=['stock'])
            messages.success(request, f'Stock for "{product.name}" set to {product.stock}.')

    return _back_to_products(request)


@admin_required
def product_toggle_availability(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product.is_available = not product.is_available
        product.save(update_fields=['is_available'])

    return _back_to_products(request)


@admin_required
def category_list(request):

    categories = Category.objects.annotate(product_count=Count('product')).order_by('name')

    return render(request, 'adminpanel/categories.html', {'categories': categories})


@admin_required
def category_add(request):

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Category name is required.')
        elif Category.objects.filter(name__iexact=name).exists():
            messages.error(request, 'That category already exists.')
        else:
            Category.objects.create(name=name)
            messages.success(request, f'"{name}" category added.')

    return redirect('admin_categories')


@admin_required
def category_edit(request, id):

    category = get_object_or_404(Category, id=id)

    if request.method == 'POST':

        name = request.POST.get('name', '').strip()

        if not name:
            messages.error(request, 'Category name is required.')
        elif Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            messages.error(request, 'That category already exists.')
        else:
            category.name = name
            category.save()
            messages.success(request, 'Category updated.')

    return redirect('admin_categories')


@admin_required
def category_delete(request, id):

    category = get_object_or_404(Category, id=id)

    if request.method == 'POST':

        if category.product_set.exists():
            messages.error(request, f'Cannot delete "{category.name}" while it still has products.')
        else:
            name = category.name
            category.delete()
            messages.success(request, f'"{name}" category deleted.')

    return redirect('admin_categories')
