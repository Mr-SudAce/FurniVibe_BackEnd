from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import *
from django.utils.crypto import get_random_string
from django.contrib import messages
from django.db import transaction

@login_required
def place_order(request):
    try:
        cart = CartModel.objects.get(user=request.user, is_active=True)
        items = cart.items.all()
        if not items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect("cart_detail")  # replace with your cart page

        shipping_address = ShippingAddressModel.objects.filter(user=request.user).last()
        if not shipping_address:
            messages.error(request, "Please provide a shipping address first.")
            return redirect("shipping_address")  # replace with your shipping address page

        total_amount = sum([item.total_price for item in items])

        # Create unique order_id
        order_id = f"FV{get_random_string(length=6, allowed_chars='0123456789')}"

        with transaction.atomic():
            order = OrderModel.objects.create(
                user=request.user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                delivery_type="standard",
                status="pending",
            )

            # Move CartItems → OrderItems
            for item in items:
                variant = item.variant
                product_name = variant.product.name
                variant_details = f"{variant.material} - {variant.color}"
                OrderItemModel.objects.create(
                    order=order,
                    product_name=product_name,
                    variant_details=variant_details,
                    price=item.price,
                    quantity=item.quantity,
                )

            # Clear cart
            cart.items.all().delete()
            cart.is_active = False
            cart.save()

        return redirect("order_success", order_id=order.id)

    except CartModel.DoesNotExist:
        messages.error(request, "You do not have an active cart.")
        return redirect("home")


@login_required
def order_success(request, order_id):
    order = get_object_or_404(OrderModel, id=order_id, user=request.user)
    return render(request, "orders/order_success.html", {"order": order})


@login_required
def my_orders(request):
    orders = OrderModel.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(OrderModel, id=order_id, user=request.user)
    items = order.items.all()
    return render(request, "orders/order_detail.html", {"order": order, "items": items})