from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import *
from .forms import *
from Handler.ViewsHandler import *


class DashboardLoginView(LoginView):
    template_name = "dashboard/auth/login.html"


class DashboardRegisterView(CreateView):
    template_name = "dashboard/auth/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("dashboard_login")



class AccountProfileView(LoginView):
    template_name = "dashboard/auth/account_profile.html"


def dashboard_home(request):
    return render(request, "dashboard/dashboard.html")


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_list(request):
    products = ProductModel.objects.all()
    return render(
        request, "dashboard/Content/product_list.html", {"products": products}
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_create(request):
    return handle_addition(
        request=request,
        form_class=ProductForm,
        model_class=ProductModel,
        unique_field="slug",  # Used for duplicate checking in handler
        success_msg="Product created successfully!",
        redirect_url="product_list",
        template_name="dashboard/product_form.html",
        list_context_name="products",  # Not strictly used by form template but required by handler
        form_context_name="form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_update(request, pk):
    return handle_update(
        request=request,
        id=pk,
        model_class=ProductModel,
        form_class=ProductForm,
        success_msg="Product updated successfully!",
        redirect_url="product_list",
        template_name="dashboard/product_form.html",
        form_context_name="form",
        object_context_name="product",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_delete(request, pk):
    return handle_deletion(
        request, pk, ProductModel, "Product deleted!", "product_list"
    )


@login_required(login_url="dashboard_login")
def account_profile(request):
    return render(
        request, "dashboard/auth/account_profile.html", {"user": request.user}
    )
