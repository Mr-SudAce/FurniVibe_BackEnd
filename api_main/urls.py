from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_app.api_urls')),
    path('', include('api_app.dashboard_urls')),
    
    # 🔐 TOKEN AUTH
    path("api/token/", obtain_auth_token, name="api_token"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





# Staff
# user name : sudace
# email: sudesh12@gmail.com
# password: sudesh12

# Staff
# user name : Dummy
# password: dummy12