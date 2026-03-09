from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Blog
from django.utils.text import slugify
from .cart import Cart
from .wishlist import Wishlist
from django.views.decorators.http import require_POST
from django.db.models import Q

def index(request):
    products = Product.objects.all()[:8]
    blogs = Blog.objects.all()[:3]
    context = {
        'products': products,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)

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
    override = request.POST.get('override', False)
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

def checkout(request):
    return render(request, 'checkout.html')

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
    return render(request, 'shop.html', context)

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

# -----------------------
# Admin Login
# -----------------------

def admin_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")

        else:
            return render(request,"admin/login.html",{
                "error":"Invalid credentials"
            })

    return render(request,"admin/login.html")


# -----------------------
# Logout
# -----------------------

def admin_logout(request):
    logout(request)
    return redirect("admin_login")

# -------------------------------
# Admin Dashboard
# -------------------------------

@login_required
def admin_dashboard(request):

    products = Product.objects.count()
    categories = Category.objects.count()

    context = {
        "products": products,
        "categories": categories
    }

    return render(request, "admin/dashboard.html", context)


# -------------------------------
# Product List
# -------------------------------
@login_required
def admin_products(request):

    products = Product.objects.all()

    return render(request,"admin/products.html",{
        "products":products
    })


# -------------------------------
# Add Product
# -------------------------------
@login_required
def admin_add_product(request):

    categories = Category.objects.all()

    if request.method == "POST":

        name = request.POST.get("name")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = Category.objects.get(id=category_id)

        slug = slugify(name)

        Product.objects.create(
            name=name,
            slug=slug,
            price=price,
            category=category,
            image=image
        )

        return redirect("admin_products")

    return render(request,"admin/add_product.html",{"categories":categories})


# -------------------------------
# Edit Product
# -------------------------------
@login_required
def admin_edit_product(request, id):

    product = get_object_or_404(Product, id=id)
    categories = Category.objects.all()

    if request.method == "POST":

        product.name = request.POST.get("name")
        product.price = request.POST.get("price")

        category_id = request.POST.get("category")
        product.category = Category.objects.get(id=category_id)

        if request.FILES.get("image"):
            product.image = request.FILES.get("image")

        product.save()

        return redirect("admin_products")

    context = {
        "product": product,
        "categories": categories
    }

    return render(request, "admin/edit_product.html", context)


# -------------------------------
# Delete Product
# -------------------------------
@login_required
def admin_delete_product(request, id):

    product = get_object_or_404(Product, id=id)
    product.delete()

    return redirect("admin_products")
@login_required
def admin_add_category(request):

    if request.method == "POST":

        name = request.POST.get("name")
        slug = request.POST.get("slug")

        Category.objects.create(
            name=name,
            slug=slug
        )

        return redirect("admin_categories")

    return render(request, "admin/add_category.html")

@login_required
def admin_categories(request):

    categories = Category.objects.all()

    return render(request, "admin/categories.html", {
        "categories": categories
    })

@login_required
def admin_delete_category(request, id):

    category = Category.objects.get(id=id)
    category.delete()

    return redirect("admin_categories")