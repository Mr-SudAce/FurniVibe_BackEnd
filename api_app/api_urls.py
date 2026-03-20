from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api_app import api_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

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
router.register(r"order-items", api_views.OrderViewSet, basename="order-item")

# --- More Images ----
router.register(r"more-images", api_views.MoreImagesViewSet)

# --- Site Configuration Endpoint ---
router.register(r"other-details", api_views.OtherDetailViewSet)

custom_urlpatterns = [
    # Orders
    path("orders/place/", api_views.PlaceOrderAPI.as_view(), name="api_place_order"),
    path("orders/my/", api_views.MyOrdersAPI.as_view(), name="api_my_orders"),
    path("orders/<int:order_id>/", api_views.OrderDetailAPI.as_view(), name="api_order_detail"),
      # ------------------------------
    # Orders - API Endpoints
    # ------------------------------
    path("orders/", api_views.AdminOrderListAPI.as_view(), name="admin_orders"),
    path("orders/<int:order_id>/", api_views.AdminOrderDetailAPI.as_view(), name="admin_order_detail"),
    path("orders/<int:order_id>/update-status/", api_views.UpdateOrderStatusAPI.as_view(), name="admin_order_update_status"),
    path("orders/<int:order_id>/update-payment/", api_views.UpdatePaymentStatusAPI.as_view(), name="admin_payment_update"),
    
    # Cart
    path("cart/", api_views.CartViewAPI.as_view(), name="api_cart"),
    path("cart/add/", api_views.AddToCartAPI.as_view(), name="api_cart_add"),
    path("cart/remove/", api_views.RemoveCartItemAPI.as_view(), name="api_cart_remove"),
    path("cart/clear/", api_views.ClearCartAPI.as_view(), name="api_cart_clear"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/", api_views.CustomAuthToken.as_view(), name="api_token_auth"),
    path("", include(custom_urlpatterns)),
    
    # 📜 API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]