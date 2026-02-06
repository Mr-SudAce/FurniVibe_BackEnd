from django.db import models
from tinymce.models import HTMLField
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, username, password, **extra_fields)

# User model
class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    username = models.CharField(max_length=100, unique=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="api_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="api_user_set",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_user = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)

    last_logout = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "first_name", "last_name", "phone_number"]

    @property
    def is_staff(self):
        return self.is_staff

    def save(self, *args, **kwargs):
        # Hash password only if not hashed
        if self.password and not self.password.startswith("pbkdf2_"):
            self.password = make_password(self.password)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.username


# Category Model
class CategoryModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
        default="images/default_category.png",
    )
    description = HTMLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Brand Model
class BrandModel(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    logo = models.ImageField(
        upload_to="brands/", blank=True, null=True, default="images/default_brand.png"
    )
    description = HTMLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Product Model
class ProductModel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)

    category = models.ForeignKey(
        "CategoryModel", related_name="products", on_delete=models.PROTECT
    )
    brand = models.ForeignKey(
        BrandModel, on_delete=models.SET_NULL, null=True, blank=True
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
        default="images/default_product.png",
    )

    moreImages = models.ManyToManyField("ProductImageModel", blank=True)

    warranty_years = models.PositiveIntegerField(default=0)
    description = HTMLField(blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["price"]),
        ]

    @property
    def discounted_price(self):
        discount = (Decimal(self.discount_percent) / 100) * self.price
        return self.price - discount

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# Product Image Model
class ProductImageModel(models.Model):
    product = models.ForeignKey(
        ProductModel, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="products/gallery/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Product Variant Model
class ProductVariantModel(models.Model):
    product = models.ForeignKey(
        ProductModel, related_name="variants", on_delete=models.CASCADE
    )

    model = models.CharField(max_length=255, blank=True, default="")
    material = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)

    weight_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    length = models.CharField(max_length=50, blank=True, null=True)
    width = models.CharField(max_length=50, blank=True, null=True)
    height = models.CharField(max_length=50, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    is_made_to_order = models.BooleanField(default=False)
    delivery_days = models.PositiveIntegerField(default=7)
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "material", "color")

    def __str__(self):
        return f"{self.product.name} - {self.material} - {self.color}"


# Product Review Model
class ProductReviewModel(models.Model):
    product = models.ForeignKey(
        ProductModel, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")


# Cart Model
class CartModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user if self.user else 'Guest'})"


# Cart Item Model
class CartItemModel(models.Model):
    cart = models.ForeignKey(CartModel, related_name="items", on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariantModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "variant")

    @property
    def total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if self._state.adding and not self.price:
            self.price = self.variant.product.discounted_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant} x {self.quantity}"


# Blog Model
class BlogModel(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="blogs/", blank=True, null=True)
    content = HTMLField(blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while BlogModel.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# OtherDetailModel
class OtherDetailModel(models.Model):
    contact = models.CharField(max_length=10, blank=False, default="")
    whatsapp = models.CharField(max_length=10, blank=False, default="")
    viber = models.CharField(max_length=10, blank=False, default="")
    facebook = models.CharField(max_length=255, blank=True, default="#")
    instagram = models.CharField(max_length=255, blank=True, default="#")
    twitter = models.CharField(max_length=255, blank=True, default="#")
    youtube = models.CharField(max_length=255, blank=True, default="#")
    email = models.EmailField(max_length=254, blank=False, default="")
    location = HTMLField(blank=True, default="https://www.google.com/maps/embed?...")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.email} - {self.contact}"


# Shipping Address Model
class ShippingAddressModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)

    address_line = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"


# Order Model
class OrderModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    shipping_address = models.ForeignKey(ShippingAddressModel, on_delete=models.PROTECT)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    delivery_type = models.CharField(
        max_length=20,
        choices=[("standard", "Standard"), ("express", "Express"), ("installation", "Delivery + Installation")],
        default="standard",
    )

    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("paid", "Paid"), ("shipped", "Shipped"), ("delivered", "Delivered"), ("cancelled", "Cancelled")],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"


# Order Item Model
class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, related_name="items", on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255)
    variant_details = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_price(self):
        return self.price * self.quantity


# Payment Model
class PaymentModel(models.Model):
    order = models.OneToOneField(OrderModel, on_delete=models.CASCADE)

    payment_method = models.CharField(
        max_length=20,
        choices=[("cod", "Cash on Delivery"), ("esewa", "eSewa"), ("khalti", "Khalti"), ("stripe", "Stripe")],
    )
    transaction_id = models.CharField(max_length=255, blank=True, null=True)

    payment_status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed"), ("refunded", "Refunded")],
        default="pending",
    )
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"


# Header Model
class HeaderModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Footer Model
class FooterModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
