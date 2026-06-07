from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('register/', views.customer_register, name='customer_register'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('orders/', views.customer_orders, name='customer_orders'),
    path('order/<int:id>/', views.customer_order_detail, name='customer_order_detail'),
    path('change-password/', views.change_password, name='customer_change_password'),
    path('forgot-password/', views.forgot_password, name='customer_forgot_password'),
]