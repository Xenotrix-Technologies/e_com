from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.db.models import Q
from store.models import Order
from django.contrib.auth import authenticate, login, logout
from .forms import CustomerLoginForm
from django.contrib import messages

def customer_login(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('index')

    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']

            if user.is_staff or user.is_superuser:
                messages.error(request, "Admin users must log in through the admin page.")
                return render(request, 'customer_login.html', {
                    'form': form,
                    'next': next_url
                })

            login(request, user)

            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)

            messages.success(request, "Login successful.")
            return redirect(next_url or 'index')
    else:
        form = CustomerLoginForm()

    return render(request, 'customer_login.html', {
        'form': form,
        'next': next_url
    })

def customer_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('customer_login')



def customer_register(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('customer_profile')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not first_name or not last_name or not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'customer_register.html')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'customer_register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'customer_register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'customer_register.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        login(request, user)
        messages.success(request, "Customer account created successfully.")
        return redirect('customer_profile')

    return render(request, 'customer_register.html')


@login_required(login_url='customer_login')
def customer_profile(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()

        if not first_name or not last_name or not email:
            messages.error(request, "All fields are required.")
            return render(request, 'customer_profile.html')

        if User.objects.filter(email=email).exclude(id=request.user.id).exists():
            messages.error(request, "Email already in use.")
            return render(request, 'customer_profile.html')

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()

        messages.success(request, "Profile updated successfully.")
        return redirect('customer_profile')

    return render(request, 'customer_profile.html')


@login_required(login_url='customer_login')
def customer_orders(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')

    # If Order model has user field
    if hasattr(Order, 'user'):
        orders = Order.objects.filter(user=request.user).order_by('-id')
    else:
        # fallback by email match
        orders = Order.objects.filter(email=request.user.email).order_by('-id')

    return render(request, 'customer_orders.html', {'orders': orders})


@login_required(login_url='customer_login')
def customer_order_detail(request, id):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')

    order = get_object_or_404(Order, id=id)

    # Protect access
    if hasattr(order, 'user') and order.user:
        if order.user != request.user:
            messages.error(request, "You are not allowed to view this order.")
            return redirect('customer_orders')
    else:
        if order.email != request.user.email:
            messages.error(request, "You are not allowed to view this order.")
            return redirect('customer_orders')

    return render(request, 'customer_order_detail.html', {'order': order})


@login_required(login_url='customer_login')
def change_password(request):
    if request.user.is_staff or request.user.is_superuser:
        return redirect('/admin/')

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed successfully.")
            return redirect('customer_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'customer_change_password.html', {'form': form})


def forgot_password(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if not username_or_email or not new_password or not confirm_password:
            messages.error(request, "All fields are required.")
            return render(request, 'customer_forgot_password.html')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'customer_forgot_password.html')

        user = User.objects.filter(
            Q(username=username_or_email) | Q(email=username_or_email),
            is_staff=False,
            is_superuser=False
        ).first()

        if not user:
            messages.error(request, "Customer account not found.")
            return render(request, 'customer_forgot_password.html')

        user.set_password(new_password)
        user.save()

        messages.success(request, "Password reset successfully. Please login.")
        return redirect('customer_login')

    return render(request, 'customer_forgot_password.html')