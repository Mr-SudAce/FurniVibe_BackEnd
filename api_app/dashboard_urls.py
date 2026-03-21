from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from . import dashboard_views

urlpatterns = [
    # Auth URLs
    path(
        "login/", dashboard_views.DashboardLoginView.as_view(), name="dashboard_login"
    ),
    path(
        "register/",
        dashboard_views.DashboardRegisterView.as_view(),
        name="dashboard_register",
    ),
    path(
        "dashboard_logout/",
        LogoutView.as_view(next_page="dashboard_login"),
        name="dashboard_logout",
    ),
    path(
        "accounts/profile/",
        dashboard_views.AccountProfileView.as_view(),
        name="accProfile",
    ),
    # Update pw
    path("settings/password/", dashboard_views.update_pw, name="update_pw"),
    # reset pw
    # 1. Submit email form
    path('password-reset/', dashboard_views.MyPasswordResetView.as_view(), name='password_reset'),
    
    # 2. Email sent confirmation
    path('password-reset/done/', dashboard_views.MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    
    # 3. Link from email (UID and Token)
    path('password-reset-confirm/<uidb64>/<token>/', dashboard_views.MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # 4. Success message
    path('password-reset-complete/', dashboard_views.MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    # Dashboard home / Product List
    path("", dashboard_views.dashboard_home, name="dashboard_home"),
    # Product CRUD URLs
    path("products/list/", dashboard_views.product_list, name="product_list"),
    path("products/create/", dashboard_views.product_create, name="product_create"),
    path(
        "products/<int:pk>/update/",
        dashboard_views.product_update,
        name="product_update",
    ),
    path(
        "products/<int:pk>/delete/",
        dashboard_views.product_delete,
        name="product_delete",
    ),
    # Category URLs
    path("categories/list/", dashboard_views.category_list, name="category_list"),
    path("categories/create/", dashboard_views.category_create, name="category_create"),
    path(
        "categories/<int:pk>/update/",
        dashboard_views.category_update,
        name="category_update",
    ),
    path(
        "categories/<int:pk>/delete/",
        dashboard_views.category_delete,
        name="category_delete",
    ),
    # Brand URLs
    path("brands/list/", dashboard_views.brand_list, name="brand_list"),
    path("brands/create/", dashboard_views.brand_create, name="brand_create"),
    path("brands/<int:pk>/update/", dashboard_views.brand_update, name="brand_update"),
    path("brands/<int:pk>/delete/", dashboard_views.brand_delete, name="brand_delete"),
    # Variant URLs
    path("variants/list/", dashboard_views.variant_list, name="variant_list"),
    path("variants/create/", dashboard_views.variant_create, name="variant_create"),
    path(
        "variants/<int:pk>/update/",
        dashboard_views.variant_update,
        name="variant_update",
    ),
    path(
        "variants/<int:pk>/delete/",
        dashboard_views.variant_delete,
        name="variant_delete",
    ),
    # Blog URLs
    path("blogs/list/", dashboard_views.blog_list, name="blog_list"),
    path("blogs/create/", dashboard_views.blog_create, name="blog_create"),
    path("blogs/<int:pk>/update/", dashboard_views.blog_update, name="blog_update"),
    path("blogs/<int:pk>/delete/", dashboard_views.blog_delete, name="blog_delete"),
    # MoreImage URLs
    path("moreImages/list/", dashboard_views.more_images_list, name="more_images_list"),
    path(
        "moreImages/create/",
        dashboard_views.more_images_create,
        name="more_images_create",
    ),
    path(
        "moreImages/<int:pk>/update/",
        dashboard_views.more_images_update,
        name="more_images_update",
    ),
    path(
        "moreImages/<int:pk>/delete/",
        dashboard_views.more_image_delete,
        name="more_images_delete",
    ),
    # Other Details URLs
    path(
        "other-details/list/",
        dashboard_views.other_detail_list,
        name="other_detail_list",
    ),
    path(
        "other-details/create/",
        dashboard_views.other_detail_create,
        name="other_detail_create",
    ),
    path(
        "other-details/<int:pk>/update/",
        dashboard_views.other_detail_update,
        name="other_detail_update",
    ),
    path(
        "other-details/<int:pk>/delete/",
        dashboard_views.other_detail_delete,
        name="other_detail_delete",
    ),
    # ------------------------------
    # Orders - Dashboard Templates
    # ------------------------------
    path("orders/list/", dashboard_views.order_list_view, name="order_list"),
    path("orders/<int:pk>/update/", dashboard_views.update_order, name="update_order"),
]
