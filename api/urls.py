from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    TrainerViewSet,
    MemberViewSet,
    MembershipViewSet,
    CustomTokenObtainPairView,
)

router = DefaultRouter()
router.register(r'trainers', TrainerViewSet, basename='trainer')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'memberships', MembershipViewSet, basename='membership')

urlpatterns = [
    # JWT аутентификация
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # API endpoints
    path('', include(router.urls)),
]
