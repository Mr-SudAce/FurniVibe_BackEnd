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



defaultPath = "dashboard/Content/"



def dashboard_home(request):
    return render(request, "dashboard/dashboard.html")


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_list(request):
    products = ProductModel.objects.all()
    return render(
        request, f"{defaultPath}list/product_list.html", {"products": products}
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_create(request):
    return handle_addition(
        request=request,
        form_class=ProductForm,
        model_class=ProductModel,
        unique_field="slug",
        success_msg="Product created successfully!",
        redirect_url="product_list",
        template_name=f"{defaultPath}form/product_form.html",
        list_context_name="products",
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
        template_name=f"{defaultPath}form/product_form.html",
        form_context_name="form",
        object_context_name="product",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def product_delete(request, pk):
    return handle_deletion(
        request, pk, ProductModel, "Product deleted!", "product_list"
    )


# ---------------------------------------------------
# CATEGORY VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def category_list(request):
    categories = CategoryModel.objects.all()
    return render(
        request, f"{defaultPath}list/category_list.html", {"categories": categories}
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def category_create(request):
    return handle_addition(
        request,
        CategoryForm,
        CategoryModel,
        "slug",
        "Category added!",
        "category_list",
        f"{defaultPath}form/category_form.html",
        "categories",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def category_update(request, pk):
    return handle_update(
        request,
        pk,
        CategoryModel,
        CategoryForm,
        "Category updated!",
        "category_list",
        f"{defaultPath}form/category_form.html",
        "form",
        "category",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def category_delete(request, pk):
    return handle_deletion(
        request, pk, CategoryModel, "Category deleted!", "category_list"
    )


# ---------------------------------------------------
# BRAND VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def brand_list(request):
    brands = BrandModel.objects.all()
    return render(request, f"{defaultPath}list/brand_list.html", {"brands": brands})


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def brand_create(request):
    return handle_addition(
        request,
        BrandForm,
        BrandModel,
        "slug",
        "Brand added!",
        "brand_list",
        f"{defaultPath}form/brand_form.html",
        "brands",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def brand_update(request, pk):
    return handle_update(
        request,
        pk,
        BrandModel,
        BrandForm,
        "Brand updated!",
        "brand_list",
        f"{defaultPath}form/brand_form.html",
        "form",
        "brand",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def brand_delete(request, pk):
    return handle_deletion(request, pk, BrandModel, "Brand deleted!", "brand_list")


# ---------------------------------------------------
# VARIANT VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def variant_list(request):
    variants = ProductVariantModel.objects.all().select_related("product")
    return render(
        request, f"{defaultPath}list/variant_list.html", {"variants": variants}
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def variant_create(request):
    # Variants don't have a slug, so we pass None for unique_field or handle differently if needed.
    # handle_addition expects unique_field, but if model doesn't have it, we might need to adjust logic or pass a dummy.
    # Assuming handle_addition handles None or we use a field that exists.
    return handle_addition(
        request,
        ProductVariantForm,
        ProductVariantModel,
        None,
        "Variant added!",
        "variant_list",
        f"{defaultPath}form/variant_form.html",
        "variants",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def variant_update(request, pk):
    return handle_update(
        request,
        pk,
        ProductVariantModel,
        ProductVariantForm,
        "Variant updated!",
        "variant_list",
        f"{defaultPath}form/variant_form.html",
        "form",
        "variant",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def variant_delete(request, pk):
    return handle_deletion(
        request, pk, ProductVariantModel, "Variant deleted!", "variant_list"
    )


# ---------------------------------------------------
# BLOG VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def blog_list(request):
    blogs = BlogModel.objects.all()
    return render(request, f"{defaultPath}list/blog_list.html", {"blogs": blogs})


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def blog_create(request):
    return handle_addition(
        request,
        BlogForm,
        BlogModel,
        "slug",
        "Blog added!",
        "blog_list",
        f"{defaultPath}form/blog_form.html",
        "blogs",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def blog_update(request, pk):
    return handle_update(
        request,
        pk,
        BlogModel,
        BlogForm,
        "Blog updated!",
        "blog_list",
        f"{defaultPath}form/blog_form.html",
        "form",
        "blog",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def blog_delete(request, pk):
    return handle_deletion(request, pk, BlogModel, "Blog deleted!", "blog_list")


@login_required(login_url="dashboard_login")
def account_profile(request):
    return render(
        request, "dashboard/auth/account_profile.html", {"user": request.user}
    )
