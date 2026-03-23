from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAdminUser
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


# Place Order API
class PlaceOrderAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            # 1. Check for Active Cart
            cart = CartModel.objects.get(user=request.user, is_active=True)
            items = cart.items.all()

            if not items.exists():
                return Response({"detail": "Cart is empty."}, status=400)

            # 2. Check for Shipping Address
            shipping_address = ShippingAddressModel.objects.filter(
                user=request.user
            ).last()
            if not shipping_address:
                return Response(
                    {
                        "detail": "Shipping address not found. Please add an address first."
                    },
                    status=400,
                )

            total_amount = sum(item.total_price for item in items)

            with transaction.atomic():
                # 3. Create Order
                order = OrderModel.objects.create(
                    user=request.user,
                    shipping_address=shipping_address,
                    total_amount=total_amount,
                    delivery_type="standard",
                    status="pending",
                )

                # 4. Create Order Items & Update Stock
                for item in items:
                    variant = item.variant
                    if not variant.is_made_to_order:
                        if variant.stock < item.quantity:
                            raise ValueError(
                                f"Stock ran out for {variant.product.name}"
                            )
                        variant.stock -= item.quantity
                        variant.save()

                    OrderItemModel.objects.create(
                        order=order,
                        product_name=variant.product.name,
                        variant_details=f"{variant.material} / {variant.color}",
                        price=item.price,
                        quantity=item.quantity,
                    )

                # 5. Create Payment record
                PaymentModel.objects.create(
                    order=order,
                    payment_method="cod",
                    payment_status="pending",
                )

                # 6. Deactivate Cart
                cart.is_active = False
                cart.save()

            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except CartModel.DoesNotExist:
            return Response({"detail": "No active cart found."}, status=404)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)


# Shipping Addresss
class ShippingAddressViewSet(viewsets.ModelViewSet):
    queryset = ShippingAddressModel.objects.all()
    serializer_class = ShippingAddressSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Users should only see their own addresses
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically link the address to the logged-in user
        serializer.save(user=self.request.user)


# My Orders API
class MyOrdersAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = OrderModel.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# Order Detail API
class OrderDetailAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Cart View API
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


# Add To Cart API
class AddToCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # We look for 'variant_id' specifically
        variant_id = request.data.get("variant_id")
        quantity = int(request.data.get("quantity", 1))

        if not variant_id:
            return Response({"detail": "variant_id is required."}, status=400)

        variant = get_object_or_404(ProductVariantModel, id=variant_id)

        # Check Stock
        if not variant.is_made_to_order and quantity > variant.stock:
            return Response(
                {"detail": f"Only {variant.stock} items available."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cart, _ = CartModel.objects.get_or_create(user=request.user, is_active=True)

        # get_or_create handles the price logic via the model's save() method
        cart_item, created = CartItemModel.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={
                "quantity": quantity,
                "price": variant.product.discounted_price,  # Uses your @property
            },
        )

        if not created:
            cart_item.quantity += quantity
            # Re-check stock for combined quantity
            if not variant.is_made_to_order and cart_item.quantity > variant.stock:
                return Response(
                    {"detail": "Not enough stock for this total quantity."}, status=400
                )
            cart_item.save()

        serializer = CartItemReadSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# Update Cart Item API
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


# Remove Cart Item API
class RemoveCartItemAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_id = request.data.get("item_id")

        cart = get_object_or_404(CartModel, user=request.user, is_active=True)
        cart_item = get_object_or_404(CartItemModel, id=item_id, cart=cart)

        cart_item.delete()

        return Response({"detail": "Item removed from cart."})


# Clear Cart API
class ClearCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = get_object_or_404(CartModel, user=request.user, is_active=True)

        cart.items.all().delete()

        return Response({"detail": "Cart cleared."})


# List All Orders
class AdminOrderListAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        orders = OrderModel.objects.all().order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


# View Single Order Detail
class AdminOrderDetailAPI(APIView):
    permission_classes = [IsStaffOrIsSuperUser]

    def get(self, request, order_id):
        order = get_object_or_404(OrderModel, id=order_id)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


# Update Order Status
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


# Update Payment Status
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
