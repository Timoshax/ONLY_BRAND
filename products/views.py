from django.shortcuts import render, get_object_or_404
from .models import Product, Category

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.all()

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(request, "products/products_list.html", {
        "category": category,
        "categories": categories,
        "products": products,
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})

from django.shortcuts import redirect
from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    cart_items = []
    total_price = 0

    for product_id, item in cart.cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_total = product.price * item['quantity']
        total_price += item_total
        cart_items.append({
            'product': product,
            'quantity': item['quantity'],
            'total_price': item_total,
        })

    return render(request, 'products/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price,
    })

def cart_add(request, product_id):
    cart = Cart(request)
    cart.add(product_id)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    return redirect('cart_detail')



from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout

def register_user(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Автоматически входим после регистрации
            return redirect('product_list')
    else:
        form = UserCreationForm()
    return render(request, 'products/register.html', {'form': form})

def login_user(request):
    """Вход на сайт."""
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'products/login.html', {'form': form})

def logout_user(request):
    """Выход из аккаунта."""
    logout(request)
    return redirect('product_list')

from .forms import OrderCreateForm
from .models import OrderItem

def order_create(request):
    """Оформление заказа"""
    cart = Cart(request)
    
    # Если корзина пуста, редиректим в каталог
    if not cart.cart:
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            # Переносим товары из корзины в OrderItem
            for product_id, item in cart.cart.items():
                product = get_object_or_404(Product, id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item['quantity']
                )
            # Очищаем корзину после создания заказа
            cart.clear()
            return render(request, 'products/order_created.html', {'order': order})
    else:
        form = OrderCreateForm()

    return render(request, 'products/order_create.html', {
        'cart': cart, 
        'form': form
    })