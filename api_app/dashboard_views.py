from django.contrib.auth.decorators import (
    user_passes_test,
    login_required,
    user_passes_test,
)
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import views as auth_views
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.urls import reverse_lazy, reverse
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from django.contrib import messages
from Handler.ViewsHandler import *
from .serializers import *
from .models import *
from .forms import *



class DashboardLoginView(APIView):
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = "dashboard/auth/login.html"
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        # FIX: Check the user's status using the boolean function, NOT the decorator
        if request.user.is_authenticated:
            if admin_and_superuser(request.user):
                return redirect("dashboard_home")
            else:
                # If they are logged in but NOT staff, don't let them stay on the login page
                # Redirect them to your main public site home or a 403 page
                messages.error(request, "Access denied. Staff only.")
                return redirect("/") 
        
        return render(request, self.template_name)

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)

        # FIX: Use your permission handler for consistency
        if user is not None and admin_and_superuser(user):
            login(request, user)
            refresh = RefreshToken.for_user(user) 
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "redirect_url": reverse("dashboard_home"),
            }, status=200)

        return Response({"detail": "Invalid credentials or not staff."}, status=401)



class DashboardRegisterView(CreateView):
    template_name = "dashboard/auth/register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("dashboard_login")

class AccountProfileView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/auth/account_profile.html"
    login_url = "dashboard_login"


defaultPath = "dashboard/Content/"

# ############################## Reset  PW ####################################
class MyPasswordResetView(auth_views.PasswordResetView):
    template_name = "dashboard/auth/reset_pw.html"
    email_template_name = "dashboard/password_reset_email.html"
    success_url = reverse_lazy("password_reset_done")


class MyPasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "dashboard/auth/reset_pw_done.html"


class MyPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "dashboard/auth/reset_pw_confirm.html"
    success_url = reverse_lazy("password_reset_complete")


class MyPasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "dashboard/auth/reset_pw_complete.html"


# ############################## Update PW ####################################



@login_required
@only_admin_and_super
def update_pw(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keeps the session alive so they aren't logged out after password change
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was successfully updated!")
            return redirect("dashboard_home")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = PasswordChangeForm(request.user)

    return render(
        request,
        "dashboard/auth/update_pw.html",
        {"form": form, "page_title": "Update Password"},
    )


@login_required
@only_admin_and_super
def edit_profile(request):
    if request.method == "POST":
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("edit_profile")
        else:
            messages.error(request, "Please correct the error below.")
    else:
        form = UserEditForm(instance=request.user)

    return render(request, "dashboard/auth/edit_profile.html", {"form": form})


@login_required(login_url="dashboard_login")
@only_admin_and_super
def dashboard_home(request):
    status_filter = request.GET.get('status', 'all')
    
    # Base counts for dashboard cards
    total_orders = OrderModel.objects.count()
    pending_orders = OrderModel.objects.filter(status="pending").count()
    completed_orders = OrderModel.objects.filter(status="paid").count()
    cancelled_orders = OrderModel.objects.filter(status="cancelled").count()
    
  # Updated View logic to reach all the way to the product name
    orders_queryset = OrderModel.objects.select_related('user', 'order_detail') \
                                        .prefetch_related('order_detail__items__product') \
                                        .all().order_by("-created_at")
    if status_filter and status_filter != 'all':
        orders_queryset = orders_queryset.filter(status=status_filter)
    
    recent_orders = orders_queryset[:5]

    context = {
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "cancelled_orders": cancelled_orders,
        "recent_orders": recent_orders,
        "current_filter": status_filter,
    }

    return render(request, "dashboard/dashboard.html", context)

def dashboard_logout(request):
    logout(request)
    return redirect("dashboard_login")

@login_required(login_url="dashboard_login")
def account_profile(request):
    return render(
        request, "dashboard/auth/account_profile.html", {"user": request.user}
    )


# ---------------------------------------------------
# PRODUCT VIEWS
# ---------------------------------------------------


@login_required(login_url="dashboard_login")
@only_admin_and_super
def product_list(request):
    products = ProductModel.objects.all()
    return render(
        request, f"{defaultPath}list/product_list.html", {"products": products}
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def product_create(request):
    return handle_addition(
        request=request,
        form_class=ProductForm,
        model_class=ProductModel,
        unique_field="slug",
        success_msg="Product created successfully!",
        redirect_url="product_create",
        template_name=f"{defaultPath}forms/product_form.html",
        list_context_name="products",
        form_context_name="form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def product_delete(request, pk):
    return handle_deletion(
        request, pk, ProductModel, "Product deleted!", "product_list"
    )


# ---------------------------------------------------
# CATEGORY VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@only_admin_and_super
def category_list(request):
    categories = CategoryModel.objects.all()
    return render(
        request, f"{defaultPath}list/category_list.html", {"categories": categories}
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def category_create(request):
    return handle_addition(
        request,
        CategoryForm,
        CategoryModel,
        "slug",
        "Category added!",
        "category_create",
        f"{defaultPath}forms/category_form.html",
        "categories",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def category_delete(request, pk):
    return handle_deletion(
        request, pk, CategoryModel, "Category deleted!", "category_list"
    )


# ---------------------------------------------------
# BRAND VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@only_admin_and_super
def brand_list(request):
    brands = BrandModel.objects.all()
    return render(request, f"{defaultPath}list/brand_list.html", {"brands": brands})


@login_required(login_url="dashboard_login")
@only_admin_and_super
def brand_create(request):
    return handle_addition(
        request,
        BrandForm,
        BrandModel,
        "slug",
        "Brand added!",
        "brand_create",
        f"{defaultPath}forms/brand_form.html",
        "brands",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def brand_delete(request, pk):
    return handle_deletion(request, pk, BrandModel, "Brand deleted!", "brand_list")


# ---------------------------------------------------
# VARIANT VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@only_admin_and_super
def variant_list(request):
    variants = ProductVariantModel.objects.all().select_related("product")
    return render(
        request, f"{defaultPath}list/variant_list.html", {"variants": variants}
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def variant_create(request):
    return handle_addition(
        request,
        ProductVariantForm,
        ProductVariantModel,
        None,
        "Variant added!",
        "variant_create",
        f"{defaultPath}forms/variant_form.html",
        "variants",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def variant_delete(request, pk):
    return handle_deletion(
        request, pk, ProductVariantModel, "Variant deleted!", "variant_list"
    )


# ---------------------------------------------------
# BLOG VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@only_admin_and_super
def blog_list(request):
    blogs = BlogModel.objects.all()
    return render(request, f"{defaultPath}list/blog_list.html", {"blogs": blogs})


@login_required(login_url="dashboard_login")
@only_admin_and_super
def blog_create(request):
    return handle_addition(
        request,
        BlogForm,
        BlogModel,
        "slug",
        "Blog added!",
        "blog_create",
        f"{defaultPath}forms/blog_form.html",
        "blogs",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def blog_delete(request, pk):
    return handle_deletion(request, pk, BlogModel, "Blog deleted!", "blog_list")


# ---------------------------------------------------
# MORE-IMAGES VIEWS
# ---------------------------------------------------
@login_required(login_url="dashboard_login")
@only_admin_and_super
def more_images_list(request):
    images = ProductImageModel.objects.all()
    return render(
        request,
        f"{defaultPath}list/more_images_list.html",
        {"images": images},
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def more_images_create(request):
    return handle_addition(
        request,
        MoreImagesForm,
        ProductImageModel,
        None,
        "Image added!",
        "more_images_create",
        f"{defaultPath}forms/more_images_form.html",
        "images",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
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
@only_admin_and_super
def more_image_delete(request, pk):
    return handle_deletion(
        request, pk, ProductImageModel, "Image deleted!", "more_images_list"
    )


# ---------------------------------------------------
# OTHER DETAILS VIEWS
# ---------------------------------------------------


@login_required(login_url="dashboard_login")
@only_admin_and_super
def other_detail_list(request):
    details = OtherDetailModel.objects.all()
    return render(
        request, f"{defaultPath}list/otherdetails_list.html", {"details": details}
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def other_detail_create(request):
    return handle_addition(
        request,
        OtherDetailForm,
        OtherDetailModel,
        "slug",
        "Other Detail added!",
        "other_detail_create",
        f"{defaultPath}forms/otherdetails_form.html",
        "otherdetails",
        "form",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def other_detail_update(request, pk):
    return handle_update(
        request,
        pk,
        OtherDetailModel,
        OtherDetailForm,
        "Other Detail updated!",
        "other_detail_list",
        f"{defaultPath}forms/otherdetails_form.html",
        "form",
        "otherdetail",
    )


@login_required(login_url="dashboard_login")
@only_admin_and_super
def other_detail_delete(request, pk):
    return handle_deletion(
        request, pk, OtherDetailModel, "Other Detail deleted!", "other_detail_list"
    )


# order
@login_required(login_url="dashboard_login")
@only_admin_and_super
def order_list_view(request):
    recent_orders = OrderModel.objects.all().order_by("-created_at")
    return render(request, f"{defaultPath}list/order_list.html", {"recent_orders": recent_orders})


def update_order(request, pk):
    order = get_object_or_404(OrderModel, pk=pk)
    if request.method == "POST":
        form = OrderUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect("order_list")
    else:
        form = OrderUpdateForm(instance=order)

    return render(
        request, f"{defaultPath}forms/order_form.html", {"form": form, "order": order}
    )

@login_required(login_url="dashboard_login")
@only_admin_and_super
def order_delete(request, pk):
    order = get_object_or_404(OrderModel, pk=pk)
    if request.method == "POST":
        order.delete()
        return redirect("order_list")
    return redirect("order_list")
