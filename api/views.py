from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from .models import Trainer, Member, Membership
from .serializers import (
    TrainerSerializer,
    MemberSerializer,
    MembershipSerializer,
    MembershipListSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Кастомное представление для получения JWT токенов"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class TrainerViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления тренерами.
    
    list: Получить список всех тренеров
    retrieve: Получить детальную информацию о тренере
    create: Создать нового тренера
    update: Обновить информацию о тренере
    partial_update: Частично обновить информацию о тренере
    destroy: Удалить тренера
    """
    queryset = Trainer.objects.all()
    serializer_class = TrainerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Trainer.objects.select_related('user').all()
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        return queryset


class MemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления участниками клуба.
    
    list: Получить список всех участников
    retrieve: Получить детальную информацию об участнике
    create: Создать нового участника
    update: Обновить информацию об участнике
    partial_update: Частично обновить информацию об участнике
    destroy: Удалить участника
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Member.objects.select_related('user').all()
        return queryset

    @action(detail=True, methods=['get'])
    def memberships(self, request, pk=None):
        """Получить все абонементы участника"""
        member = self.get_object()
        memberships = member.memberships.all()
        serializer = MembershipSerializer(memberships, many=True)
        return Response(serializer.data)


class MembershipViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления абонементами.
    
    list: Получить список всех абонементов
    retrieve: Получить детальную информацию об абонементе
    create: Создать новый абонемент
    update: Обновить информацию об абонементе
    partial_update: Частично обновить информацию об абонементе
    destroy: Удалить абонемент
    """
    queryset = Membership.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return MembershipListSerializer
        return MembershipSerializer

    def get_queryset(self):
        queryset = Membership.objects.select_related('member__user', 'trainer__user').all()
        
        # Фильтрация по участнику
        member_id = self.request.query_params.get('member_id', None)
        if member_id:
            queryset = queryset.filter(member_id=member_id)
        
        # Фильтрация по тренеру
        trainer_id = self.request.query_params.get('trainer_id', None)
        if trainer_id:
            queryset = queryset.filter(trainer_id=trainer_id)
        
        # Фильтрация по статусу
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Фильтрация по типу абонемента
        membership_type = self.request.query_params.get('membership_type', None)
        if membership_type:
            queryset = queryset.filter(membership_type=membership_type)
        
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Получить список активных абонементов"""
        active_memberships = self.get_queryset().filter(status='active')
        page = self.paginate_queryset(active_memberships)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(active_memberships, many=True)
        return Response(serializer.data)
