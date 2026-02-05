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
]   