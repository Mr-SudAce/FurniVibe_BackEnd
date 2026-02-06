from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.utils.text import slugify
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test


# -------------------------------
# PERMISSIONS
# -------------------------------
def is_staff(user):
    return user.is_authenticated and (
        user.is_staff or user.is_staff or user.is_superuser
    )


def is_superuser(user):
    return user.is_authenticated and (user.is_superuser or user.is_superuser)


def admin_or_super_required(view_func):
    return user_passes_test(is_staff, login_url="dashboard_login")(view_func)


def web_superadmin_required(view_func):
    return user_passes_test(is_superuser, login_url="dashboard_login")(view_func)


# -------------------------------
# UTILITY FUNCTION
# -------------------------------
def hash_password_if_present(instance, form):
    if hasattr(instance, "password"):
        pw = form.cleaned_data.get("password")
        if pw:
            instance.password = make_password(pw)


# -------------------------------
# COUNT HANDLER
# -------------------------------
@admin_or_super_required
def handle_count(request, model_class, load_temp="dashboard.html"):
    return model_class.objects.count()


# -------------------------------
# ADDITION HANDLER
# -------------------------------
@admin_or_super_required
def handle_addition(
    request,
    form_class,
    model_class,
    unique_field,
    success_msg,
    redirect_url,
    template_name,
    list_context_name,
    form_context_name,
):
    form = form_class(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    instance = form.save(commit=False)

                    # Extra validation for User
                    if model_class.__name__ == "User":
                        hash_password_if_present(instance, form)
                        
                        # Auto-generate username if not present
                        if not instance.username:
                            base_username = f"{instance.first_name}{instance.last_name}".lower()
                            username = base_username
                            counter = 1
                            while model_class.objects.filter(username=username).exists():
                                username = f"{base_username}{counter}"
                                counter += 1
                            instance.username = username
                        instance.is_staff = True
                        instance.is_superuser = False
                        instance.is_user = False

                    instance.save()
                    form.save_m2m()
                    messages.success(request, success_msg)
                    return redirect(redirect_url)
            except IntegrityError as e:
                messages.error(request, f"Duplicate entry detected: {e}")
            except Exception as e:
                messages.error(request, f"Something went wrong: {e}")
        else:
            messages.error(request, "Invalid form data.")

    queryset = model_class.objects.all()
    return render(
        request,
        template_name,
        {
            list_context_name: queryset,
            form_context_name: form,
        },
    )


# -------------------------------
# UPDATE HANDLER
# -------------------------------
@admin_or_super_required
def handle_update(
    request,
    id,
    model_class,
    form_class,
    success_msg="Updated successfully",
    redirect_url="/",
    template_name="",
    form_context_name="form",
    object_context_name="object",
):
    instance = get_object_or_404(model_class, id=id)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            try:
                with transaction.atomic():
                    instance = form.save(commit=False)

                    # Extra for User: hash password if changed
                    if model_class.__name__ == "User":
                        hash_password_if_present(instance, form)

                    instance.save()
                    form.save_m2m()
                    messages.success(request, success_msg)
                    return redirect(redirect_url)
            except Exception as e:
                messages.error(request, f"Update failed: {e}")
        else:
            messages.error(request, "Invalid form data.")
    else:
        form = form_class(instance=instance)

    return render(
        request,
        template_name,
        {
            form_context_name: form,
            object_context_name: instance,
        },
    )


# -------------------------------
# DELETION HANDLER
# -------------------------------
@web_superadmin_required
def handle_deletion(
    request,
    id,
    model_class,
    success_msg="Deleted successfully",
    redirect_url="/",
):
    instance = get_object_or_404(model_class, id=id)

    try:
        with transaction.atomic():
            instance.delete()
            messages.success(request, success_msg)
    except Exception as e:
        messages.error(request, f"Delete failed: {e}")

    return redirect(redirect_url)
