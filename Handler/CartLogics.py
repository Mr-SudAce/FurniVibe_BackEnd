from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes # type: ignore
from rest_framework.response import Response
from rest_framework import status
from Handler.ApiViewHandler import *
from api.models import *

# Create Cart Logic
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def CreateCart(request):
    cart, created = CartModel.objects.get_or_create(
        user=request.user,
        is_active=True
    )

    return Response(
        {
            "status": True,
            "message": "Cart created" if created else "Cart already exists",
            "cart_id": cart.id,
        },
        status=status.HTTP_201_CREATED,
    )


# Get all Cart Logic
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetAllCart(request):
    carts = CartModel.objects.filter(user=request.user)

    data = []
    for cart in carts:
        data.append({
            "cart_id": cart.id,
            "is_active": cart.is_active,
            "created_at": cart.created_at,
        })

    return Response(
        {"status": True, "data": data},
        status=status.HTTP_200_OK,
    )



# Get Cart by ID Logic
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def GetCartById(request, id):
    cart = get_object_or_404(CartModel, id=id, user=request.user)

    items = CartItemModel.objects.filter(cart=cart)

    cart_items = []
    for item in items:
        cart_items.append({
            "item_id": item.id,
            "variant": str(item.variant),
            "quantity": item.quantity,
            "price": item.price,
            "total_price": item.total_price,
        })

    return Response(
        {
            "status": True,
            "cart_id": cart.id,
            "items": cart_items,
        },
        status=status.HTTP_200_OK,
    )



# Update Cart Logic
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def UpdateCart(request, id):
    cart = get_object_or_404(CartModel, id=id, user=request.user)

    variant_id = request.data.get("variant_id")
    quantity = int(request.data.get("quantity", 1))

    if not variant_id:
        return Response(
            {"status": False, "message": "variant_id is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    variant = get_object_or_404(ProductVariantModel, id=variant_id)

    try:
        with transaction.atomic():
            cart_item, created = CartItemModel.objects.get_or_create(
                cart=cart,
                variant=variant,
                defaults={"quantity": quantity},
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

    except Exception as e:
        return Response(
            {
                "status": False,
                "message": "Failed to update cart",
                "error": str(e),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "status": True,
            "message": "Cart updated 🛒",
            "variant": str(variant),
            "quantity": cart_item.quantity,
        },
        status=status.HTTP_200_OK,
    )


# Delete Cart Logic
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def DeleteCart(request, id):
    cart = get_object_or_404(CartModel, id=id, user=request.user)
    cart.delete()

    return Response(
        {
            "status": True,
            "message": "Cart deleted ❌",
        },
        status=status.HTTP_200_OK,
    )
