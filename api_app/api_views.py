from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from api_app.models import *

from api_app.serializers import *

from Handler.ApiViewHandler import *

from .permissions import IsStaffOrIsSuperUser, IsSuperUser


# ---------------------------------------------------
# USER VIEWSET
# ---------------------------------------------------


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsStaffOrIsSuperUser()]

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
