from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Trainer, Member, Membership


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Кастомный сериализатор для JWT токенов с дополнительными полями"""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Добавляем дополнительные поля в токен
        token['username'] = user.username
        token['email'] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователя"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class TrainerSerializer(serializers.ModelSerializer):
    """Сериализатор для тренера"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = [
            'id', 'user', 'user_id', 'specialization', 'experience_years',
            'phone', 'bio', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class MemberSerializer(serializers.ModelSerializer):
    """Сериализатор для участника"""
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True,
        required=False
    )
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Member
        fields = [
            'id', 'user', 'user_id', 'phone', 'date_of_birth',
            'address', 'emergency_contact', 'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class MembershipSerializer(serializers.ModelSerializer):
    """Сериализатор для абонемента"""
    member = MemberSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(
        queryset=Member.objects.all(),
        source='member',
        write_only=True
    )
    trainer = TrainerSerializer(read_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(),
        source='trainer',
        write_only=True,
        required=False,
        allow_null=True
    )
    membership_type_display = serializers.CharField(source='get_membership_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'member', 'member_id', 'membership_type', 'membership_type_display',
            'start_date', 'end_date', 'price', 'status', 'status_display',
            'trainer', 'trainer_id', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MembershipListSerializer(serializers.ModelSerializer):
    """Упрощенный сериализатор для списка абонементов"""
    member_name = serializers.CharField(source='member.user.get_full_name', read_only=True)
    trainer_name = serializers.CharField(source='trainer.user.get_full_name', read_only=True, allow_null=True)
    membership_type_display = serializers.CharField(source='get_membership_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'member_name', 'membership_type', 'membership_type_display',
            'start_date', 'end_date', 'price', 'status', 'status_display',
            'trainer_name', 'created_at'
        ]
