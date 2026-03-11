from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product, Category, Blog, Order, OrderItem
from django.core.paginator import Paginator
from django.utils.text import slugify
from .cart import Cart
from .wishlist import Wishlist
from django.views.decorators.http import require_POST
from django.db.models import Q, Sum

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

    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_sales = Order.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    low_stock_products = Product.objects.filter(stock__lt=5)

    recent_orders = Order.objects.order_by('-created_at')[:5]
    top_products = Product.objects.all()[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'low_stock_products': low_stock_products,
        'recent_orders': recent_orders,
        'top_products': top_products,
    }

    return render(request,'admin/dashboard.html',context)


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

        Product.objects.create(
            name=request.POST['name'],
            slug=request.POST['slug'],
            description=request.POST['description'],
            price=request.POST['price'],
            stock=request.POST['stock'],
            category_id=request.POST['category'],
            image=request.FILES.get('image'),
            is_available=request.POST.get('is_available') == 'on'
        )

        return redirect('admin_products')

    return render(request,'admin/add_product.html',{'categories':categories})


# -------------------------------
# Edit Product
# -------------------------------
@login_required
def admin_edit_product(request, id):

    product = Product.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == "POST":

        product.name = request.POST['name']
        product.slug = request.POST['slug']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.stock = request.POST['stock']
        product.category_id = request.POST['category']
        product.is_available = request.POST.get('is_available') == 'on'

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()

        return redirect('admin_products')

    return render(request,'admin/edit_product.html',{
        'product':product,
        'categories':categories
    })


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

@login_required

def inventory(request):
    search = request.GET.get('search')
    products = Product.objects.all().order_by('-created_at')
    if search:
        products = products.filter(name__icontains=search)
    paginator = Paginator(products,10)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    return render(request,"admin/inventory.html",{"products":products})

def admin_order_detail(request,id):

    order = Order.objects.get(id=id)

    return render(request,'admin/order_detail.html',{
        'order':order
    })

def admin_orders(request):

    orders = Order.objects.all().order_by('-id')
    context = {
        'orders': orders
    }
    return render(request, 'admin/orders.html', context)

def admin_reports(request):

    total_revenue = Order.objects.aggregate(
        total=Sum("total_price")
    )["total"] or 0

    products_sold = OrderItem.objects.aggregate(
        total=Sum("quantity")
    )["total"] or 0

    low_stock = Product.objects.filter(stock__lte=5).count()

    out_stock = Product.objects.filter(stock=0).count()


    top_products = (
        OrderItem.objects
        .values("product__name","product__image")
        .annotate(
            total_qty=Sum("quantity"),
            total_sales=Sum("price")
        )
        .order_by("-total_qty")[:5]
    )


    low_stock_products = Product.objects.filter(stock__lte=5)


    chart_labels = ["Jan","Feb","Mar","Apr","May","Jun"]
    chart_data = [1200,1900,3000,2500,2200,3200]


    context = {

        "total_revenue": total_revenue,
        "products_sold": products_sold,
        "low_stock": low_stock,
        "out_stock": out_stock,
        "top_products": top_products,
        "low_stock_products": low_stock_products,
        "chart_labels": chart_labels,
        "chart_data": chart_data,

    }

    return render(request,"admin/reports.html",context)