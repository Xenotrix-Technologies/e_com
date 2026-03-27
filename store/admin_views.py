from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from .models import Product, Category, Order, OrderItem
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.contrib import messages
from django.contrib.auth.models import User

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

@login_required
def admin_change_password(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'admin/change_password.html', {
        'form': form
    })

def admin_forgot_password(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username_or_email or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'admin/forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'admin/forgot_password.html')

        user = User.objects.filter(
            Q(username=username_or_email) | Q(email=username_or_email),
            is_staff=True
        ).first()

        if not user:
            messages.error(request, "Admin account not found.")
            return render(request, 'admin/forgot_password.html')

        user.set_password(new_password)
        user.save()

        messages.success(request, "Password reset successfully. Please login.")
        return redirect('admin_login')

    return render(request, 'admin/forgot_password.html')

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

    return render(request,'admin/order_details.html',{
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
        .filter(product__isnull=False)
        .values("product__name", "product__image")
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
