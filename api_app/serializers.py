from rest_framework import serializers
from api_app.models import *
from rest_framework.validators import UniqueValidator
from django.contrib.auth import get_user_model
from django.db import transaction
import time
from django.contrib.auth.hashers import make_password

User = get_user_model()

# ----------------- User Read Serializer -----------------
class UserSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "status",
            "is_active",
            "created_at",
            "last_login",
        ]

    def get_status(self, obj):
        if obj.is_superuser:
            return "Super Admin"
        elif obj.is_staff:
            return "Admin"
        return "User"



# ----------------- User Create Serializer -----------------
class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="A user with that email already exists.")
        ],
    )
    phone_number = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="A user with that phone number already exists.")]
    )
    password = serializers.CharField(write_only=True, min_length=8)
    is_staff = serializers.BooleanField(default=False, write_only=True)
    is_superuser = serializers.BooleanField(default=False, write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "password",
            "is_staff",
            "is_superuser",
        ]
        read_only_fields = ["username"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        # Roles from input are ignored during creation.
        validated_data.pop("is_staff", None)
        validated_data.pop("is_superuser", None)
        # Auto-generate username
        base_username = f"{validated_data['first_name']}{validated_data['last_name']}".lower()
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User(
            username=username,
            **validated_data
        )

        user.password = make_password(password)

        # New users are always created as 'Admin'
        user.is_staff = True
        user.is_superuser = False
        user.is_user = False
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        is_staff = validated_data.pop("is_staff", None)
        is_superuser = validated_data.pop("is_superuser", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.password = make_password(password)

        if is_superuser:
            instance.is_superuser = True
            instance.is_staff = True
            instance.is_user = False
        elif is_staff:
            instance.is_staff = True
            instance.is_user = False

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


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddressModel
        fields = [
            "id",
            "full_name",
            "phone",
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


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_address = ShippingAddressSerializer(read_only=True)

    class Meta:
        model = OrderModel
        fields = [
            "id",
            "status",
            "delivery_type",
            "total_amount",
            "shipping_address",
            "items",
            "created_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    shipping_address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(
        choices=["cod", "esewa", "khalti", "stripe"]
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

            # 🔒 STOCK LOCK + PRICE CALC
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

            # 🧾 CREATE ORDER
            order = OrderModel.objects.create(
                user=user,
                shipping_address=shipping_address,
                total_amount=total_amount,
                delivery_type=validated_data["delivery_type"],
                status="pending",
            )

            # 📦 ORDER ITEMS (SNAPSHOT)
            for item in cart_items:
                OrderItemModel.objects.create(
                    order=order,
                    product_name=item.variant.product.name,
                    variant_details=f"{item.variant.material} / {item.variant.color}",
                    price=item.price,
                    quantity=item.quantity,
                )

            # 💳 PAYMENT
            PaymentModel.objects.create(
                order=order,
                payment_method=validated_data["payment_method"],
                payment_status="pending",
            )

            # 🧹 CLOSE CART
            cart.is_active = False
            cart.save()

            cart_items.delete()

            return order


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentModel
        fields = [
            "id",
            "payment_method",
            "transaction_id",
            "payment_status",
            "paid_at",
        ]


class OtherdetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherDetailModel
        fields = [
            "id",
            "facebook",
            "instagram",
            "twitter",
            "youtube",
            "email",
            "location",
            "contact",
            "whatsapp",
            "viber",
        ]


class VariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariantModel
        fields = [
            "id",
            "product",
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


class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="author", write_only=True
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