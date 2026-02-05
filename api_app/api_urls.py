from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api_app import api_views

router = DefaultRouter()
router.register(r"users", api_views.UserViewSet, basename="user")
router.register(r"categories", api_views.CategoryViewSet)
router.register(r"brands", api_views.BrandViewSet)
router.register(r"products", api_views.ProductViewSet)
router.register(r"variants", api_views.ProductVariantViewSet)
router.register(r"blogs", api_views.BlogViewSet)
router.register(r"orders", api_views.OrderViewSet)
router.register(r"other-details", api_views.OtherDetailViewSet)


urlpatterns = [
    path("", include(router.urls)),
    path("api-token-auth/", api_views.CustomAuthToken.as_view(), name="api_token_auth"),
]