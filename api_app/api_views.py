from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from .permissions import IsStaffOrIsSuperUser
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from Handler.ApiViewHandler import *
from rest_framework import viewsets
from rest_framework import filters
from django.db import transaction
from api_app.serializers import *
from api_app.models import *


# --- Custom Permission ---
class IsStaffOrIsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and (request.user.is_staff or request.user.is_superuser)
        )


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


# RegisterAPI
class RegisterAPI(generics.CreateAPIView):
    queryset = UserModel.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {"message": "User created successfully!", "user": serializer.data},
            status=status.HTTP_201_CREATED,
        )


# --- User ViewSet ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    authentication_classes = [JWTAuthentication]
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


# CATEGORY VIEWSET
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = CategoryModel.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# BRAND VIEWSET
class BrandViewSet(viewsets.ModelViewSet):
    queryset = BrandModel.objects.all()
    serializer_class = BrandSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# PRODUCT VIEWSET
class ProductViewSet(viewsets.ModelViewSet):
    queryset = ProductModel.objects.select_related(
        "category", "brand"
    ).prefetch_related("images", "variants", "reviews", "reviews__user")
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
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
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# MORE IMAGES VIEWSET
class MoreImagesViewSet(viewsets.ModelViewSet):
    queryset = ProductImageModel.objects.all()
    serializer_class = ProductImageSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# VARIANT VIEWSET
class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariantModel.objects.select_related("product").all()
    serializer_class = ProductVariantSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# BLOG VIEWSET
class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogModel.objects.select_related("author").all()
    serializer_class = BlogSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# ORDER VIEWSET
class OrderViewSet(viewsets.ModelViewSet):
    queryset = OrderModel.objects.select_related(
        "user", "shipping_address", "payment"
    ).prefetch_related("items")
    serializer_class = OrderSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "paymentmodel__payment_status", "delivery_type"]
    search_fields = ["id", "user__username", "user__email", "shipping_address__phone"]


# OTHER DETAIL VIEWSET
class OtherDetailViewSet(viewsets.ModelViewSet):
    queryset = OtherDetailModel.objects.all()
    serializer_class = OtherdetailSerializer
    authentication_classes = [JWTAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [IsStaffOrIsSuperUser()]


# CUSTOM LOGIN TOKEN
class DashboardDataView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"stats": "Top Secret Admin Data"})


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # We look for 'username' or 'email' in the request body
        login_id = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not login_id or not password:
            return Response(
                {"error": "Username/Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Look up the user by email OR username
        user = (
            UserModel.objects.filter(email=login_id).first()
            or UserModel.objects.filter(username=login_id).first()
        )

        if user and user.check_password(password):
            if not user.is_active:
                return Response(
                    {"error": "User is inactive"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Standard Django way to handle tokens
            token, _ = Token.objects.get_or_create(user=user)

            return Response(
                {
                    "token": token.key,
                    "user_id": user.pk,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"non_field_errors": ["Unable to log in with provided credentials."]},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PlaceOrderAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        # 1. Get the active cart and check if it's empty
        cart = CartModel.objects.filter(user=user, is_active=True).first()
        if not cart or not cart.items.exists():
            return Response({"detail": "Your cart is empty."}, status=400)

        # 2. Get the latest shipping address for this user
        shipping_address = ShippingAddressModel.objects.filter(user=user).last()
        if not shipping_address:
            return Response({"detail": "Shipping address required."}, status=400)

        try:
            with transaction.atomic():
                # 3. Calculate Total Amount based on CURRENT CartItem prices
                # (Remember: our UpdateCartItemAPI already refreshed these prices)
                total_amount = sum(
                    item.price * item.quantity for item in cart.items.all()
                )

                # Apply your shipping logic (matches frontend: Free over 5000, else 150)
                shipping_fee = 0 if total_amount > 5000 else 150
                final_total = total_amount + shipping_fee

                # 4. Create the Order
                order = OrderModel.objects.create(
                    user=user,
                    shipping_address=shipping_address,
                    total_amount=final_total,
                    status="pending",
                )

                # 5. Move items from Cart to OrderItems (Snapshoting details)
                for cart_item in cart.items.all():
                    # Double check stock one last time before finalizing
                    if not cart_item.variant.is_made_to_order:
                        if cart_item.variant.stock < cart_item.quantity:
                            raise Exception(
                                f"Item {cart_item.variant.product.name} went out of stock."
                            )

                        # Deduct stock
                        cart_item.variant.stock -= cart_item.quantity
                        cart_item.variant.save()

                    OrderItemModel.objects.create(
                        order=order,
                        product_name=cart_item.variant.product.name,
                        variant_details=f"{cart_item.variant.material} - {cart_item.variant.color}",
                        price=cart_item.price,  # The price at the time of purchase
                        quantity=cart_item.quantity,
                    )

                # 6. Deactivate the cart so the user starts fresh next time
                cart.is_active = False
                cart.save()

                return Response(
                    {
                        "detail": "Order placed successfully!",
                        "order_id": order.id,
                        "total_amount": float(final_total),
                    },
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddressModel.objects.all()
    serializer_class = ShippingAddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MyOrdersAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CartViewAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = CartModel.objects.prefetch_related(
            "items",
            "items__cart",
            "items__variant",
            "items__variant__product",
            "items__variant__product__images",
        ).get_or_create(user=request.user, is_active=True)

        serializer = CartItemReadSerializer(cart.items.all(), many=True)
        total_amount = sum(item.total_price for item in cart.items.all())

        return Response({"cart_items": serializer.data, "total_amount": total_amount})


class AddToCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"detail": "product_id is required."}, status=400)

        product = get_object_or_404(ProductModel, id=product_id)
        variant = product.variants.first()

        if not variant:
            return Response(
                {"detail": "No variant found for this product."}, status=404
            )
        cart, _ = CartModel.objects.get_or_create(user=request.user, is_active=True)

        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": 0,
                "price": product.discounted_price,
            },
        )
        new_total_quantity = cart_item.quantity + quantity
        if not variant.is_made_to_order and new_total_quantity > variant.stock:
            return Response(
                {"detail": f"Only {variant.stock} items available in total."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Update Item
        cart_item.quantity = new_total_quantity
        cart_item.price = product.discounted_price
        cart_item.save()

        serializer = CartItemReadSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        quantity = request.data.get("quantity")

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {"detail": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST
            )

        if quantity < 1:
            return Response(
                {"detail": "Quantity must be at least 1"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Ensure we only update items belonging to the logged-in user's active cart
        cart_item = get_object_or_404(
            CartItemModel, id=item_id, cart__user=request.user, cart__is_active=True
        )
        variant = cart_item.variant

        # Check stock levels
        if not variant.is_made_to_order and quantity > variant.stock:
            return Response(
                {"detail": f"Only {variant.stock} items in stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            cart_item.quantity = quantity
            cart_item.price = variant.product.discounted_price
            cart_item.save()

            return Response(
                {
                    "detail": "Cart updated successfully",
                    "item_id": cart_item.id,
                    "quantity": cart_item.quantity,
                    "unit_price": float(cart_item.price),
                    "total_price": float(cart_item.price * cart_item.quantity),
                },
                status=status.HTTP_200_OK,
            )


class RemoveCartItemAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")
        cart = get_object_or_404(CartModel, user=request.user, is_active=True)
        cart_item = get_object_or_404(CartItemModel, id=item_id, cart=cart)
        cart_item.delete()
        return Response(
            {"detail": "Item removed from cart."}, status=status.HTTP_200_OK
        )


class ClearCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(CartModel, user=request.user, is_active=True)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."}, status=status.HTTP_200_OK)


class AdminOrderListAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        orders = OrderModel.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class AdminOrderDetailAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


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
