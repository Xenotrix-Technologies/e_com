from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.blog_details, name='blog_details'),
    path('contact/', views.contact, name='contact'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('cart/', views.shopping_cart, name='shopping_cart'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),
    path('search/', views.search, name='search'),
    path('checkout/', views.checkout, name='checkout'),
    path('wishlist/', views.wishlist_detail, name='wishlist_detail'),
    path('wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),

    #admin urls
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/add-product/', views.admin_add_product, name='admin_add_product'),
    path('dashboard/edit-product/<int:id>/', views.admin_edit_product, name='admin_edit_product'),
    path('dashboard/delete-product/<int:id>/', views.admin_delete_product, name='admin_delete_product'),

    # category management
    path('admin/categories/', views.admin_categories, name='admin_categories'),
    path('admin/add-category/', views.admin_add_category, name='admin_add_category'),
    path('admin/delete-category/<int:id>/', views.admin_delete_category, name='admin_delete_category'),

]
