from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    RegisterView,
    MeView,
    TrainerViewSet,
    MemberProfileViewSet,
    MembershipViewSet,
    TrainingClassViewSet,
    BookingViewSet,
)

router = DefaultRouter()
router.register(r'trainers', TrainerViewSet, basename='trainer')
router.register(r'members', MemberProfileViewSet, basename='member')
router.register(r'memberships', MembershipViewSet, basename='membership')
router.register(r'classes', TrainingClassViewSet, basename='trainingclass')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    path('', include(router.urls)),
]
