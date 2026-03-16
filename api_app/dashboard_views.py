from django.shortcuts import render
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
def account_profile(request):
    return render(
        request, "dashboard/auth/account_profile.html", {"user": request.user}
    )


# ---------------------------------------------------
# PRODUCT VIEWS
# ---------------------------------------------------


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
        template_name=f"{defaultPath}forms/product_form.html",
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
        template_name=f"{defaultPath}forms/product_form.html",
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
        f"{defaultPath}forms/category_form.html",
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
        f"{defaultPath}forms/category_form.html",
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
        f"{defaultPath}forms/brand_form.html",
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
        f"{defaultPath}forms/brand_form.html",
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
    return handle_addition(
        request,
        ProductVariantForm,
        ProductVariantModel,
        None,
        "Variant added!",
        "variant_list",
        f"{defaultPath}forms/variant_form.html",
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
        f"{defaultPath}forms/variant_form.html",
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
        f"{defaultPath}forms/blog_form.html",
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
        f"{defaultPath}forms/blog_form.html",
        "form",
        "blog",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def blog_delete(request, pk):
    return handle_deletion(request, pk, BlogModel, "Blog deleted!", "blog_list")


# ---------------------------------------------------
# MORE-IMAGES VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def more_images_list(request):
    images = ProductImageModel.objects.all()
    return render(
        request,
        f"{defaultPath}list/more_images_list.html",
        {"images": images},
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def more_images_create(request):
    return handle_addition(
        request,
        MoreImagesForm,
        ProductImageModel,
        None,
        "Image added!",
        "more_images_list",
        f"{defaultPath}forms/more_images_form.html",
        "images",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def more_images_update(request, pk):
    return handle_update(
        request,
        pk,
        ProductImageModel,
        MoreImagesForm,
        "Image updated!",
        "more_images_list",
        f"{defaultPath}forms/more_images_form.html",
        "form",
        "image",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def more_image_delete(request, pk):
    return handle_deletion(
        request, pk, ProductImageModel, "Image deleted!", "more_images_list"
    )


# ---------------------------------------------------
# OTHER DETAILS VIEWS
# ---------------------------------------------------


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def other_detail_list(request):
    details = OtherDetailModel.objects.all()
    return render(
        request, f"{defaultPath}list/otherdetails_list.html", {"details": details}
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def other_detail_create(request):
    return handle_addition(
        request,
        OtherDetailForm,
        OtherDetailModel,
        "slug",
        "Other Detail added!",
        "other_detail_list",
        f"{defaultPath}forms/otherdetails_form.html",
        "otherdetails",
        "form",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def other_detail_update(request, pk):
    return handle_update(
        request,
        pk,
        OtherDetailModel,
        OtherDetailForm,
        "Other Detail updated!",
        "otherdetail_list",
        f"{defaultPath}forms/otherdetails_form.html",
        "form",
        "otherdetail",
    )


@login_required(login_url="dashboard_login")
@user_passes_test(is_staff, login_url="dashboard_login")
def other_detail_delete(request, pk):
    return handle_deletion(
        request, pk, OtherDetailModel, "Other Detail deleted!", "other_detail_list"
    )
