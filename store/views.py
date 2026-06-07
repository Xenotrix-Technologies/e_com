from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import Product, Category, Blog, Order, OrderItem
from django.core.paginator import Paginator
from django.utils.text import slugify
from .cart import Cart
from .wishlist import Wishlist
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

from .models import ContactMessage

def index(request):
    products = Product.objects.all()[:8]
    blogs = Blog.objects.all()[:3]
    context = {
        'products': products,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)

def about(request):
    return render(request, "about.html")

def shop(request):
    products = Product.objects.filter(is_available=True)
    categories = Category.objects.all()

    # Category filter
    selected_category = request.GET.get('category', '')
    if selected_category:
        products = products.filter(category__slug=selected_category)

    # Price range filter
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    if min_price:
        try:
            products = products.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            products = products.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'shop_fixed.html', context)

def blog(request):
    blogs = Blog.objects.all()
    context = {
        'blogs': blogs,
    }
    return render(request, 'blog.html', context)

def blog_details(request, slug):
    blog = Blog.objects.get(slug=slug)
    context = {
        'blog': blog,
    }
    return render(request, 'blog-details.html', context)

def contact(request):
    return render(request, 'contact.html')

def product_details(request, slug):
    product = Product.objects.get(slug=slug)
    context = {
        'product': product,
    }
    return render(request, 'shop-details.html', context)

def shopping_cart(request):
    cart = Cart(request)
    return render(request, 'shopping-cart.html', {'cart': cart})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override') == 'True'
    cart.add(product=product, quantity=quantity, override_quantity=override)
    return redirect('shopping_cart')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('shopping_cart')

@require_POST
def cart_update(request):
    cart = Cart(request)
    for product_id, quantity in request.POST.items():
        if product_id.startswith('quantity_'):
            id = product_id.replace('quantity_', '')
            product = get_object_or_404(Product, id=id)
            cart.add(product=product, quantity=int(quantity), override_quantity=True)
    return redirect('shopping_cart')
@login_required
def checkout(request):
    cart = Cart(request)
    if not request.user.is_authenticated:
        return redirect('customer_login')
        
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        country = request.POST.get('country', '').strip()
        address_line_1 = request.POST.get('address_line_1', '').strip()
        address_line_2 = request.POST.get('address_line_2', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        postcode = request.POST.get('postcode', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        order_notes = request.POST.get('order_notes', '').strip()
        payment_method = request.POST.get('payment_method', '').strip()
        terms = request.POST.get('terms')
        create_account = request.POST.get('create_account')
        password = request.POST.get('password', '').strip()

        # Check cart
        if len(cart) == 0:
            messages.error(request, "Your cart is empty.")
            return render(request, 'checkout.html', {'cart': cart})

        # Check required fields
        required_fields = {
            'First name': first_name,
            'Last name': last_name,
            'Country': country,
            'Street address': address_line_1,
            'City': city,
            'State': state,
            'Postcode': postcode,
            'Phone': phone,
            'Email': email,
            'Payment method': payment_method,
        }

        for field_name, value in required_fields.items():
            if not value:
                messages.error(request, f"{field_name} is required.")
                return render(request, 'checkout.html', {'cart': cart})

        # Terms checkbox
        if not terms:
            messages.error(request, "You must agree to the terms and conditions.")
            return render(request, 'checkout.html', {'cart': cart})

        # If create account checked, password required
        if create_account and not password:
            messages.error(request, "Password is required when creating an account.")
            return render(request, 'checkout.html', {'cart': cart})

        order = Order.objects.create(
            user=request.user,
            first_name=first_name,
            last_name=last_name,
            country=country,
            address_line_1=address_line_1,
            address_line_2=address_line_2,
            city=city,
            state=state,
            postcode=postcode,
            phone=phone,
            email=email,
            order_notes=order_notes,
            payment_method=payment_method,
            total_price=cart.get_total_price()
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                quantity=item['quantity'],
                price=item['price']
            )

        cart.clear()
        messages.success(request, "Order placed successfully.")
        return redirect('checkout_success')

    return render(request, 'checkout.html', {'cart': cart})

def checkout_success(request):
    return render(request, 'checkout_success.html')

def search(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(category__name__icontains=query)
        ).distinct()
    else:
        products = Product.objects.none()
    
    categories = Category.objects.all()
    context = {
        'products': products,
        'categories': categories,
        'query': query,
    }
    return render(request, 'shop_fixed.html', context)

def wishlist_detail(request):
    return render(request, 'wishlist.html')

def wishlist_add(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    wishlist.add(product)
    return redirect('wishlist_detail')

def wishlist_remove(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    wishlist.remove(product)
    return redirect('wishlist_detail')

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        subject = request.POST.get("subject", "").strip()
        message = request.POST.get("message", "").strip()

        if not name or not email or not subject or not message:
            messages.error(request, "All fields are required.")
            return render(request, "contact.html")

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        full_message = f"""
New Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""

        try:
            send_mail(
                subject=f"Contact Form: {subject}",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=False,
            )
        except Exception:
            pass

        messages.success(request, "Your message has been sent successfully.")
        return redirect("contact")

    return render(request, "contact.html")


