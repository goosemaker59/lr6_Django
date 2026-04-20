from django.contrib.auth.models import User
from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Trainer, MemberProfile, Membership, TrainingClass, Booking
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    TrainerListSerializer,
    TrainerDetailSerializer,
    TrainerWriteSerializer,
    MemberProfileSerializer,
    MemberProfileWriteSerializer,
    MembershipSerializer,
    TrainingClassListSerializer,
    TrainingClassDetailSerializer,
    BookingSerializer,
    BookingCreateSerializer,
)
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly


# ──────────────────────────────────────────────
#  Custom pagination
# ──────────────────────────────────────────────
class StandardPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ──────────────────────────────────────────────
#  Auth: Register
# ──────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя.
    Не требует аутентификации.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# ──────────────────────────────────────────────
#  Me (текущий пользователь)
# ──────────────────────────────────────────────
class MeView(generics.RetrieveUpdateAPIView):
    """
    Получение и обновление данных текущего авторизованного пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# ──────────────────────────────────────────────
#  Trainer ViewSet
# ──────────────────────────────────────────────
class TrainerViewSet(viewsets.ModelViewSet):
    """
    CRUD для тренеров фитнес-клуба.

    list: Список всех тренеров (с пагинацией и фильтрацией)
    retrieve: Детальная информация о тренере
    create: Создать профиль тренера (только администраторы)
    update: Обновить профиль тренера (только администраторы)
    partial_update: Частичное обновление тренера (только администраторы)
    destroy: Удалить тренера (только администраторы)
    """
    queryset = Trainer.objects.select_related('user').all()
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specialization', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'bio']
    ordering_fields = ['experience_years', 'hourly_rate', 'created_at']
    ordering = ['user__last_name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainerListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return TrainerWriteSerializer
        return TrainerDetailSerializer

    @swagger_auto_schema(
        operation_summary="Список тренеров",
        operation_description="Возвращает список тренеров с пагинацией. "
                               "Фильтрация по specialization и is_active. "
                               "Поиск по имени и биографии."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Детальная информация о тренере")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создать тренера (только администраторы)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновить тренера (только администраторы)")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление тренера")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удалить тренера (только администраторы)")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Расписание занятий тренера",
        operation_description="Возвращает все будущие занятия данного тренера."
    )
    @action(detail=True, methods=['get'], url_path='schedule')
    def schedule(self, request, pk=None):
        """Расписание занятий конкретного тренера."""
        from django.utils import timezone
        trainer = self.get_object()
        classes = trainer.classes.filter(
            scheduled_at__gte=timezone.now(),
            is_cancelled=False
        ).order_by('scheduled_at')
        serializer = TrainingClassListSerializer(classes, many=True)
        return Response(serializer.data)


# ──────────────────────────────────────────────
#  MemberProfile ViewSet
# ──────────────────────────────────────────────
class MemberProfileViewSet(viewsets.ModelViewSet):
    """
    CRUD для профилей участников клуба.

    Владелец профиля может читать и редактировать свои данные.
    Администратор имеет доступ ко всем профилям.
    """
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['gender', 'goal']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    ordering_fields = ['created_at', 'updated_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MemberProfile.objects.select_related('user').all()
        return MemberProfile.objects.filter(user=user)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsOwnerOrAdmin()]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MemberProfileWriteSerializer
        return MemberProfileSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(operation_summary="Список профилей участников")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Профиль участника")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создать профиль участника")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновить профиль участника")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление профиля")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удалить профиль участника")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Записи на занятия участника",
        operation_description="Возвращает все записи на занятия данного участника."
    )
    @action(detail=True, methods=['get'], url_path='bookings')
    def member_bookings(self, request, pk=None):
        """Все записи участника на занятия."""
        profile = self.get_object()
        bookings = profile.bookings.select_related('training_class').all()
        page = self.paginate_queryset(bookings)
        if page is not None:
            serializer = BookingSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# ──────────────────────────────────────────────
#  Membership ViewSet
# ──────────────────────────────────────────────
class MembershipViewSet(viewsets.ModelViewSet):
    """
    CRUD для абонементов.

    Участник видит только свои абонементы.
    Администратор видит все.
    """
    serializer_class = MembershipSerializer
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['plan', 'status', 'member']
    ordering_fields = ['start_date', 'end_date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Membership.objects.select_related('member__user').all()
        try:
            profile = user.member_profile
            return Membership.objects.filter(member=profile)
        except MemberProfile.DoesNotExist:
            return Membership.objects.none()

    def get_permissions(self):
        if self.action in ['destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    @swagger_auto_schema(operation_summary="Список абонементов")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Детали абонемента")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создать абонемент")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновить абонемент")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление абонемента")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удалить абонемент (только администраторы)")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ──────────────────────────────────────────────
#  TrainingClass ViewSet
# ──────────────────────────────────────────────
class TrainingClassViewSet(viewsets.ModelViewSet):
    """
    CRUD для групповых занятий.

    Все авторизованные пользователи могут просматривать занятия.
    Создание/обновление/удаление — только администраторы.
    """
    queryset = TrainingClass.objects.select_related('trainer__user').all()
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['trainer', 'difficulty', 'is_cancelled']
    search_fields = ['name', 'description', 'room']
    ordering_fields = ['scheduled_at', 'price', 'capacity']
    ordering = ['scheduled_at']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return TrainingClassListSerializer
        return TrainingClassDetailSerializer

    @swagger_auto_schema(
        operation_summary="Список занятий",
        operation_description="Возвращает список групповых занятий с пагинацией. "
                               "Фильтрация по trainer, difficulty, is_cancelled."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Детальная информация о занятии")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Создать занятие (только администраторы)")
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновить занятие")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление занятия")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Удалить занятие (только администраторы)")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Список участников занятия",
        operation_description="Возвращает список всех записавшихся участников."
    )
    @action(detail=True, methods=['get'], url_path='participants', permission_classes=[IsAdminUser])
    def participants(self, request, pk=None):
        """Список участников конкретного занятия."""
        training_class = self.get_object()
        bookings = training_class.bookings.filter(
            status='confirmed'
        ).select_related('member__user')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


# ──────────────────────────────────────────────
#  Booking ViewSet
# ──────────────────────────────────────────────
class BookingViewSet(viewsets.ModelViewSet):
    """
    CRUD для записей на занятия.

    Участник управляет своими записями.
    Администратор видит все записи.
    """
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'training_class', 'member']
    ordering_fields = ['booked_at', 'status']
    ordering = ['-booked_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Booking.objects.select_related(
                'member__user', 'training_class'
            ).all()
        try:
            profile = user.member_profile
            return Booking.objects.filter(member=profile).select_related('training_class')
        except MemberProfile.DoesNotExist:
            return Booking.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        try:
            profile = self.request.user.member_profile
        except MemberProfile.DoesNotExist:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Сначала создайте профиль участника.')
        serializer.save(member=profile)

    @swagger_auto_schema(operation_summary="Список записей на занятия")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Детали записи")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Записаться на занятие",
        operation_description="Создаёт запись текущего авторизованного участника на занятие. "
                               "Автоматически привязывает к профилю участника."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Обновить запись")
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Частичное обновление записи (например, добавить отзыв)")
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Отменить/удалить запись")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Отменить запись",
        operation_description="Меняет статус записи на 'cancelled' без удаления из базы."
    )
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """Отменить запись на занятие."""
        booking = self.get_object()
        if booking.status == 'cancelled':
            return Response(
                {'detail': 'Запись уже отменена.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        booking.status = 'cancelled'
        booking.save()
        return Response({'detail': 'Запись отменена.'}, status=status.HTTP_200_OK)
