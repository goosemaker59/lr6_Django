from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# ──────────────────────────────────────────────
#  Swagger schema
# ──────────────────────────────────────────────
schema_view = get_schema_view(
    openapi.Info(
        title="Fitness Club API",
        default_version='v1',
        description=(
            "RESTful API для управления фитнес-клубом.\n\n"
            "**Аутентификация:** JWT Bearer token.\n\n"
            "1. Выполните `POST /api/token/` с логином и паролем.\n"
            "2. Скопируйте значение поля `access`.\n"
            "3. Нажмите кнопку **Authorize** (🔒) выше и введите: `Bearer <ваш_токен>`.\n"
            "4. Теперь все запросы будут авторизованы."
        ),
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@fitnessclub.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # App API
    path('api/', include('fitness_club.urls')),

    # Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # ReDoc (alternative docs)
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Raw schema
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
