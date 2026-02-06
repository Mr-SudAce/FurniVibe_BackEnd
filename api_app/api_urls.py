from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api_app import api_views

# Initialize the default router
router = DefaultRouter()

# --- User Endpoint ---
router.register(r"users", api_views.UserViewSet, basename="user")

# --- Product Catalog Endpoints ---
router.register(r"categories", api_views.CategoryViewSet)
router.register(r"brands", api_views.BrandViewSet)
router.register(r"products", api_views.ProductViewSet)
router.register(r"variants", api_views.ProductVariantViewSet)

# --- Content and Order Management Endpoints ---
router.register(r"blogs", api_views.BlogViewSet)
router.register(r"orders", api_views.OrderViewSet)

# --- Site Configuration Endpoint ---
router.register(r"other-details", api_views.OtherDetailViewSet)


urlpatterns = [
    # Include all the URLs registered with the router under the main API endpoint
    path("", include(router.urls)),
    # Custom endpoint for obtaining an authentication token
    path("auth/token/", api_views.CustomAuthToken.as_view(), name="api_token_auth"),
]
