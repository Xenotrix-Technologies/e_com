from django.urls import path
from . import views, admin_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_details, name='blog_details'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('cart/', views.shopping_cart, name='shopping_cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/success/', views.checkout_success, name='checkout_success'),
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about, name='about'),

    #admin urls
    path('admin-login/', admin_views.admin_login, name='admin_login'),
    path('admin-logout/', admin_views.admin_logout, name='admin_logout'),
    path('admin-change-password/', admin_views.admin_change_password, name='admin_change_password'),
    path('admin-forgot-password/', admin_views.admin_forgot_password, name='admin_forgot_password'),
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/inventory/', admin_views.inventory, name='inventory'),
    path('dashboard/products/', admin_views.admin_products, name='admin_products'),
    path('dashboard/add-product/', admin_views.admin_add_product, name='admin_add_product'),
    path('dashboard/edit-product/<int:id>/', admin_views.admin_edit_product, name='admin_edit_product'),
    path('dashboard/delete-product/<int:id>/', admin_views.admin_delete_product, name='admin_delete_product'),

    # category management
    path('admin/categories/', admin_views.admin_categories, name='admin_categories'),
    path('admin/add-category/', admin_views.admin_add_category, name='admin_add_category'),
    path('admin/delete-category/<int:id>/', admin_views.admin_delete_category, name='admin_delete_category'),
    path("dashboard/reports/", admin_views.admin_reports, name="admin_reports"),

    # order management
    path('dashboard/orders/', admin_views.admin_orders, name='admin_orders'),
    path('dashboard/order/<int:id>/', admin_views.admin_order_detail, name='admin_order_detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)