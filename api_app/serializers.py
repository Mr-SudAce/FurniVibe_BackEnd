from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from django.db import transaction
from api_app.models import *
from django.utils import timezone
from .models import *


class UserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "password",
            "status",
            "is_active",
            "is_user",
            "is_staff",
            "created_at",
        ]
        read_only_fields = ["created_at", "is_staff", "is_superuser"]

    def get_status(self, obj):
        if obj.is_superuser:
            return "Super Admin"
        return "Admin" if obj.is_staff else "User"

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(),
                message="A user with this email exists.",
            )
        ],
    )
    phone_number = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=UserModel.objects.all(), message="Phone number already exists."
            )
        ],
    )
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = UserModel
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "is_staff",
            "is_user",
        ]
        read_only_fields = ["username"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.pop("email")

        first_name = validated_data.get("first_name", "").lower().strip()
        last_name = validated_data.get("last_name", "").lower().strip()
        base_username = f"{first_name}{last_name}"

        if not base_username:
            base_username = "user"

        username = base_username
        counter = 1
        while UserModel.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = UserModel.objects.create_user(
            email=email, username=username, password=password, **validated_data
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        is_staff = validated_data.pop("is_staff", None)
        is_user = validated_data.pop("is_user", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        if is_staff is not None:
            instance.is_staff = is_staff
            if is_staff:
                instance.is_user = False
            else:
                instance.is_user = True

        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ["id", "name", "slug", "image", "description"]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandModel
        fields = ["id", "name", "slug"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImageModel
        fields = ["id", "image"]


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantModel
        fields = [
            "id",
            "model",
            "material",
            "color",
            "length",
            "width",
            "height",
            "weight_kg",
            "stock",
            "is_made_to_order",
            "delivery_days",
        ]


class ProductReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ProductReviewModel
        fields = [
            "id",
            "user",
            "rating",
            "comment",
            "created_at",
        ]


class ProductSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=ProductModel.objects.all(), message="Name already exists"
            )
        ]
    )

    # WRITE (IDs)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=CategoryModel.objects.all(),
        source="category",
        write_only=True,
    )
    brand_id = serializers.PrimaryKeyRelatedField(
        queryset=BrandModel.objects.all(),
        source="brand",
        write_only=True,
        required=False,
    )
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)

    discounted_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "name",
            "slug",
            "category",
            "image",
            "category_id",
            "brand",
            "brand_id",
            "price",
            "discount_percent",
            "discounted_price",
            "warranty_years",
            "description",
            "is_featured",
            "images",
            "variants",
            "reviews",
        ]


class CartItemSerializer(serializers.ModelSerializer):
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=CartModel.objects.all(),
        source="cart",
        write_only=True,
    )

    variant_id = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariantModel.objects.all(),
        source="variant",
        write_only=True,
    )

    product = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItemModel
        fields = [
            "id",
            "cart_id",
            "variant_id",
            "product",
            "quantity",
            "price",
            "total_price",
        ]
        read_only_fields = ["price"]

    def get_product(self, obj):
        return ProductSerializer(obj.variant.product).data

    def get_total_price(self, obj):
        return obj.total_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    cart_total = serializers.SerializerMethodField()

    class Meta:
        model = CartModel
        fields = ["id", "items", "cart_total", "created_at"]

    def get_cart_total(self, obj):
        return sum(item.total_price for item in obj.items.all())


# Read Only Version
class CartItemReadSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItemModel
        fields = ["id", "product", "quantity", "price", "total_price"]

    def get_product(self, obj):
        return ProductSerializer(obj.variant.product).data

    def get_total_price(self, obj):
        return obj.total_price


class CartReadSerializer(serializers.ModelSerializer):
    items = CartItemReadSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = CartModel
        fields = ["id", "user", "items", "total_amount", "created_at"]

    def get_total_amount(self, obj):
        return sum([item.total_price for item in obj.items.all()])


# Read Only Version ^


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddressModel
        fields = [
            "id",
            "name",
            "phone_number",
            "address_line",
            "city",
            "state",
            "postal_code",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItemModel
        fields = [
            "id",
            "product_name",
            "variant_details",
            "price",
            "quantity",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.total_price


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = [
            "payment_method",
            "transaction_id",
            "payment_status",
            "paid_at",
        ]


class OrderSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "user",
            "shipping_address",
            "total_amount",
            "delivery_type",
            "status",
            "payment",
            "items",
            "created_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=["cod", "esewa", "bank_transfer"], default="cod"
    )
    delivery_type = serializers.ChoiceField(
        choices=["standard", "express", "installation"], default="standard"
    )

    def validate_cart_id(self, value):
        if not CartModel.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid or inactive cart.")
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        cart = CartModel.objects.select_for_update().get(
            id=validated_data["cart_id"], is_active=True
        )
        shipping_address = ShippingAddressModel.objects.get(
            id=validated_data["shipping_address_id"], user=user
        )
        cart_items = CartItemModel.objects.select_related(
            "variant", "variant__product"
        ).filter(cart=cart)
        if not cart_items.exists():
            raise serializers.ValidationError("Cart is empty.")

        with transaction.atomic():
            total_amount = 0
            for item in cart_items:
                variant = ProductVariantModel.objects.select_for_update().get(
                    id=item.variant.id
                )
                if not variant.is_made_to_order and variant.stock < item.quantity:
                    raise serializers.ValidationError(
                        f"Not enough stock for {variant.product.name}"
                    )
                if not variant.is_made_to_order:
                    variant.stock -= item.quantity
                    variant.save()

                total_amount += item.total_price

            order = OrderModel.objects.create(
                user=user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                delivery_type=validated_data["delivery_type"],
                status="pending",
            )
            for item in cart_items:
                OrderItemModel.objects.create(
                    order=order,
                    product_name=item.variant.product.name,
                    variant_details=f"{item.variant.material} / {item.variant.color}",
                    price=item.price,
                    quantity=item.quantity,
                )

            PaymentModel.objects.create(
                order=order,
                payment_method=validated_data["payment_method"],
                payment_status="pending",
                transaction_id=None,
                paid_at=None,
            )

            # 🧹 CLOSE CART
            cart.is_active = False
            cart.save()
            cart_items.delete()
            return order


class OtherdetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherDetailModel
        fields = [
            "id",
            "site_name",
            "site_logo",
            "site_tag",
            "facebook",
            "instagram",
            "twitter",
            "tiktok",
            "youtube",
            "email",
            "location",
            "contact",
            "whatsapp",
            "viber",
        ]


class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), source="author", write_only=True
    )

    class Meta:
        model = BlogModel
        fields = [
            "id",
            "title",
            "slug",
            "image",
            "content",
            "author",
            "author_id",
            "is_active",
            "created_at",
            "updated_at",
        ]
