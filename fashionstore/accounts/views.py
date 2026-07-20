from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from .forms import RegisterForm
from django.shortcuts import get_object_or_404
from .models import Order, Product

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')

    else:
        form = RegisterForm()

    return render(request, 'register.html', {
        'form': form
    })


def user_login(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('/')



def order_detail(request, id):
    order = get_object_or_404(Order, id=id)

    return render(
        request,
        'order_detail.html',
        {'order': order}
    )

User = get_user_model()

def dashboard(request):

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
    }

    return render(request, 'dashboard.html', context)