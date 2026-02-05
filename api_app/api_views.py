from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api_app.models import (
    User,
    CategoryModel,
    BrandModel,
    ProductModel,
    ProductVariantModel,
    BlogModel,
    OrderModel,
    OtherDetailModel,
)

from api_app.serializers import (
    UserSerializer,
    UserCreateSerializer,
    CategorySerializer,
    BrandSerializer,
    ProductSerializer,
    VariantSerializer,
    BlogSerializer,
    OrderSerializer,
    OtherdetailSerializer,
)

from Handler.ApiViewHandler import (
    handle_create,
    handle_getAll,
    handle_get_byid,
    handle_update,
    handle_deletion,
)

from .permissions import IsStaffOrIsSuperUser, IsSuperUser


# ---------------------------------------------------
# USER VIEWSET
# ---------------------------------------------------


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action == "create":
            return [AllowAny()]

        if self.action in ["update", "partial_update", "destroy"]:
            return [IsSuperUser()]

        return [IsStaffOrIsSuperUser()]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return UserCreateSerializer
        return UserSerializer

    def list(self, request, *args, **kwargs):
        return handle_getAll(
            model=User,
            serializer_class=UserSerializer,
            not_found_message="No users found",
        )

    def create(self, request, *args, **kwargs):
        return handle_create(
            serializer_class=UserCreateSerializer,
            request=request,
            success_message="User created successfully",
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        return handle_get_byid(User, UserSerializer, pk, "User not found")

    def update(self, request, pk=None, *args, **kwargs):
        return handle_update(
            User, UserCreateSerializer, pk, request, "User updated successfully"
        )

    def destroy(self, request, pk=None, *args, **kwargs):
        return handle_deletion(User, pk, "User deleted successfully")


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
    queryset = ProductModel.objects.all()
    serializer_class = ProductSerializer
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]


# ---------------------------------------------------
# VARIANT VIEWSET
# ---------------------------------------------------


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariantModel.objects.all()
    serializer_class = VariantSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]


# ---------------------------------------------------
# BLOG VIEWSET
# Public read / Admin write
# ---------------------------------------------------


class BlogViewSet(viewsets.ModelViewSet):
    queryset = BlogModel.objects.all()
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
    queryset = OrderModel.objects.all()
    serializer_class = OrderSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]


# ---------------------------------------------------
# OTHER DETAIL VIEWSET
# ---------------------------------------------------


class OtherDetailViewSet(viewsets.ModelViewSet):
    queryset = OtherDetailModel.objects.all()
    serializer_class = OtherdetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrIsSuperUser]


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
