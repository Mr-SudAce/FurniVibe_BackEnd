from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from django.db import transaction
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from api_app.models import *
from rest_framework.decorators import action
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from api_app.serializers import *

from Handler.ApiViewHandler import *
from django.contrib.auth import get_user_model
from .permissions import IsStaffOrIsSuperUser


# ---------------------------------------------------
# USER VIEWSET
# ---------------------------------------------------
User = get_user_model()


# --- Custom Permission ---
class IsStaffOrIsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and (request.user.is_staff or request.user.is_superuser)
        )


# --- Login View (Supports Email or Username) ---
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        login_id = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not login_id or not password:
            return Response(
                {"error": "Username/Email and password required"}, status=400
            )

        user = (
            User.objects.filter(email=login_id).first()
            or User.objects.filter(username=login_id).first()
        )

        if user and user.check_password(password):
            if not user.is_active:
                return Response({"error": "User is inactive"}, status=400)

            try:
                token = Token.objects.get(user=user)
            except Token.DoesNotExist:
                token = Token.objects.create(user=user)

            return Response(
                {
                    "token": token.key,
                    "user_id": user.pk,
                    "email": user.email,
                    "username": user.username,
                }
            )

        return Response(
            {"non_field_errors": ["Unable to log in with provided credentials."]},
            status=status.HTTP_400_BAD_REQUEST,
        )


# --- User ViewSet ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ["username", "email", "phone_number"]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]
        if self.action == "me":
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]

    @action(
        detail=False,
        methods=["get", "patch", "put"],
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     authentication_classes = [TokenAuthentication]

#     def get_serializer_class(self):
#         if self.action == 'create':
#             return UserCreateSerializer
#         return UserSerializer

#     # Allow admin filtering
#     filter_backends = [filters.SearchFilter]
#     search_fields = ['username', 'email', 'phone_number']

#     def get_permissions(self):
#         if self.action == "create":
#             return [AllowAny()]
#         # Strictly protect list/retrieve to avoid exposing user data publicly
#         # Users can see their own profile via a specific /me endpoint or logic, but standard list should be admin only
#         return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# CATEGORY VIEWSET
# Public read / Admin write
# ---------------------------------------------------


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# BRAND VIEWSET
# ---------------------------------------------------


class BrandViewSet(viewsets.ModelViewSet):
    queryset = BrandModel.objects.all()
    serializer_class = BrandSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# PRODUCT VIEWSET
# ---------------------------------------------------


class ProductViewSet(viewsets.ModelViewSet):
    # Optimized QuerySet to prevent N+1 problems
    queryset = ProductModel.objects.select_related(
        "category", "brand"
    ).prefetch_related("images", "variants", "reviews", "reviews__user")
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]

    # ✅ UI ENHANCEMENT: Search, Filter, Sort
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["category", "brand", "is_featured", "is_active"]
    search_fields = ["name", "description", "brand__name", "category__name"]
    ordering_fields = ["price", "created_at", "name", "discount_percent"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# MORE IMAGES VIEWSET
# ---------------------------------------------------


class MoreImagesViewSet(viewsets.ModelViewSet):
    queryset = ProductImageModel.objects.all()
    serializer_class = ProductImageSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# VARIANT VIEWSET
# ---------------------------------------------------


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariantModel.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]


# ---------------------------------------------------
# BLOG VIEWSET
# Public read / Admin write
# ---------------------------------------------------


class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogModel.objects.select_related("author").all()
    serializer_class = BlogSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# ORDER VIEWSET
# Fully Protected
# ---------------------------------------------------


class OrderViewSet(viewsets.ModelViewSet):
    # Prefetch items and select related address for efficient dashboard rendering
    queryset = OrderModel.objects.select_related(
        "user", "shipping_address", "payment"
    ).prefetch_related("items")
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]

    # ✅ Dashboard Search
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "paymentmodel__payment_status", "delivery_type"]
    search_fields = ["id", "user__username", "user__email", "shipping_address__phone"]


# ---------------------------------------------------
# OTHER DETAIL VIEWSET
# ---------------------------------------------------


class OtherDetailViewSet(viewsets.ModelViewSet):
    queryset = OtherDetailModel.objects.all()
    serializer_class = OtherdetailSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# CUSTOM LOGIN TOKEN
# ---------------------------------------------------


class CustomAuthToken(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
                "is_staff": user.is_staff,
            }
        )


# -----------------------------
# Place Order API
# -----------------------------
class PlaceOrderAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            cart = CartModel.objects.get(user=request.user, is_active=True)
            items = cart.items.all()

            if not items.exists():
                return Response(
                    {"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST
                )

            shipping_address = ShippingAddressModel.objects.filter(
                user=request.user
            ).last()
            if not shipping_address:
                return Response(
                    {"detail": "Shipping address not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total_amount = 0

            with transaction.atomic():
                order = OrderModel.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    total_amount=0,
                    delivery_type="standard",
                    status="pending",
                )

                for item in items:
                    variant = item.variant

                    # ✅ STOCK CHECK + REDUCE
                    if not variant.is_made_to_order:
                        if variant.stock < item.quantity:
                            return Response(
                                {
                                    "detail": f"Not enough stock for {variant.product.name}"
                                },
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                        variant.stock -= item.quantity
                        variant.save()

                    total_amount += item.total_price

                    OrderItemModel.objects.create(
                        order=order,
                        product_name=variant.product.name,
                        variant_details=f"{variant.material} - {variant.color}",
                        price=item.price,
                        quantity=item.quantity,
                    )

                # ✅ UPDATE TOTAL
                order.total_amount = total_amount
                order.save()

                # ✅ CREATE PAYMENT
                PaymentModel.objects.create(
                    order=order,
                    payment_method="cod",
                    payment_status="pending",
                )

                # ✅ CLEAR CART
                cart.items.all().delete()
                cart.is_active = False
                cart.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CartModel.DoesNotExist:
            return Response(
                {"detail": "No active cart found."}, status=status.HTTP_400_BAD_REQUEST
            )


# -----------------------------
# My Orders API
# -----------------------------
class MyOrdersAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# -----------------------------
# Order Detail API
# -----------------------------
class OrderDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# -----------------------------
# Cart View API
# -----------------------------
class CartViewAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = CartModel.objects.prefetch_related(
            "items",
            "items__variant",
            "items__variant__product",
            "items__variant__product__images",
        ).get_or_create(user=request.user, is_active=True)

        serializer = CartItemReadSerializer(cart.items.all(), many=True)
        total_amount = sum(item.total_price for item in cart.items.all())

        return Response({"cart_items": serializer.data, "total_amount": total_amount})


# -----------------------------
# Add To Cart API
# -----------------------------
class AddToCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        variant = get_object_or_404(ProductVariantModel, id=variant_id)

        if quantity > variant.stock:
            return Response(
                {"detail": f"Only {variant.stock} items available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = CartModel.objects.get_or_create(user=request.user, is_active=True)

        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={"quantity": quantity, "price": variant.product.discounted_price},
        )

        if not created:
            cart_item.quantity += quantity

            if cart_item.quantity > variant.stock:
                return Response(
                    {"detail": f"Only {variant.stock} items available."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            cart_item.save()

        serializer = CartItemReadSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -----------------------------
# Update Cart Item API
# -----------------------------
class UpdateCartItemAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        quantity = int(request.data.get("quantity", 1))

        cart = get_object_or_404(CartModel, user=request.user, is_active=True)
        cart_item = get_object_or_404(CartItemModel, id=item_id, cart=cart)

        if quantity > cart_item.variant.stock:
            return Response(
                {"detail": "Not enough stock."}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"detail": "Cart updated successfully"})


# -----------------------------
# Remove Cart Item API
# -----------------------------
class RemoveCartItemAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")

        cart = get_object_or_404(CartModel, user=request.user, is_active=True)
        cart_item = get_object_or_404(CartItemModel, id=item_id, cart=cart)

        cart_item.delete()

        return Response({"detail": "Item removed from cart."})


# -----------------------------
# Clear Cart API
# -----------------------------
class ClearCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(CartModel, user=request.user, is_active=True)

        cart.items.all().delete()

        return Response({"detail": "Cart cleared."})


# -----------------------------
# List All Orders
# -----------------------------
class AdminOrderListAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def get(self, request):
        orders = OrderModel.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# -----------------------------
# View Single Order Detail
# -----------------------------
class AdminOrderDetailAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# -----------------------------
# Update Order Status
# -----------------------------
class UpdateOrderStatusAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def post(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id)
        status_choice = request.data.get("status")
        if status_choice not in dict(OrderModel._meta.get_field("status").choices):
            return Response(
                {"detail": "Invalid status choice."}, status=status.HTTP_400_BAD_REQUEST
            )
        order.status = status_choice
        order.save()
        return Response(
            {"detail": f"Order #{order_id} status updated to {status_choice}."}
        )


# -----------------------------
# Update Payment Status
# -----------------------------
class UpdatePaymentStatusAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def post(self, request, order_id):
        payment = get_object_or_404(PaymentModel, order_id=order_id)
        payment_status = request.data.get("payment_status")
        if payment_status not in dict(
            PaymentModel._meta.get_field("payment_status").choices
        ):
            return Response(
                {"detail": "Invalid payment status choice."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment.payment_status = payment_status
        payment.save()
        return Response(
            {"detail": f"Payment for Order #{order_id} updated to {payment_status}."}
        )
