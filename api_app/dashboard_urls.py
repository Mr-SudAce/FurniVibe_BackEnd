from django.urls import path
from django.contrib.auth.views import LogoutView

from . import dashboard_views

urlpatterns = [
    # Auth URLs
    path("login/", dashboard_views.DashboardLoginView.as_view(), name="dashboard_login"),
    path("register/", dashboard_views.DashboardRegisterView.as_view(), name="dashboard_register"),
    path("logout/", LogoutView.as_view(next_page="dashboard_login"), name="dashboard_logout"),
    path("accounts/profile/", dashboard_views.AccountProfileView.as_view(), name="accProfile"),
    

    # Dashboard home / Product List
    path("", dashboard_views.dashboard_home, name="dashboard_home"),

    # Product CRUD URLs
    path("products/list/", dashboard_views.product_list, name="product_list"),
    path("products/create/", dashboard_views.product_create, name="product_create"),
    path("products/<int:pk>/update/", dashboard_views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", dashboard_views.product_delete, name="product_delete"),

    # Category URLs
    path("categories/list/", dashboard_views.category_list, name="category_list"),
    path("categories/create/", dashboard_views.category_create, name="category_create"),
    path("categories/<int:pk>/update/", dashboard_views.category_update, name="category_update"),
    path("categories/<int:pk>/delete/", dashboard_views.category_delete, name="category_delete"),

    # Brand URLs
    path("brands/list/", dashboard_views.brand_list, name="brand_list"),
    path("brands/create/", dashboard_views.brand_create, name="brand_create"),
    path("brands/<int:pk>/update/", dashboard_views.brand_update, name="brand_update"),
    path("brands/<int:pk>/delete/", dashboard_views.brand_delete, name="brand_delete"),

    # Variant URLs
    path("variants/list/", dashboard_views.variant_list, name="variant_list"),
    path("variants/create/", dashboard_views.variant_create, name="variant_create"),
    path("variants/<int:pk>/update/", dashboard_views.variant_update, name="variant_update"),
    path("variants/<int:pk>/delete/", dashboard_views.variant_delete, name="variant_delete"),

    # Blog URLs
    path("blogs/list/", dashboard_views.blog_list, name="blog_list"),
    path("blogs/create/", dashboard_views.blog_create, name="blog_create"),
    path("blogs/<int:pk>/update/", dashboard_views.blog_update, name="blog_update"),
    path("blogs/<int:pk>/delete/", dashboard_views.blog_delete, name="blog_delete"),
]   