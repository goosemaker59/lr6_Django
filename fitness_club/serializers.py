from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Trainer, MemberProfile, Membership, TrainingClass, Booking


# ──────────────────────────────────────────────
#  User / Auth
# ──────────────────────────────────────────────
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя."""
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Подтверждение пароля')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'Пароли не совпадают.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


# ──────────────────────────────────────────────
#  Trainer
# ──────────────────────────────────────────────
class TrainerListSerializer(serializers.ModelSerializer):
    """Компактный сериализатор для списков."""
    full_name = serializers.SerializerMethodField()
    specialization_display = serializers.CharField(
        source='get_specialization_display', read_only=True
    )

    class Meta:
        model = Trainer
        fields = [
            'id', 'full_name', 'specialization', 'specialization_display',
            'experience_years', 'hourly_rate', 'is_active', 'photo',
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class TrainerDetailSerializer(serializers.ModelSerializer):
    """Полный сериализатор тренера."""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    specialization_display = serializers.CharField(
        source='get_specialization_display', read_only=True
    )
    classes_count = serializers.SerializerMethodField()

    class Meta:
        model = Trainer
        fields = [
            'id', 'user', 'full_name', 'specialization', 'specialization_display',
            'bio', 'experience_years', 'hourly_rate', 'photo', 'is_active',
            'classes_count', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_classes_count(self, obj):
        return obj.classes.count()


class TrainerWriteSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления тренера."""
    class Meta:
        model = Trainer
        fields = [
            'specialization', 'bio', 'experience_years',
            'hourly_rate', 'photo', 'is_active',
        ]


# ──────────────────────────────────────────────
#  MemberProfile
# ──────────────────────────────────────────────
class MemberProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    goal_display = serializers.CharField(source='get_goal_display', read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    active_membership = serializers.SerializerMethodField()

    class Meta:
        model = MemberProfile
        fields = [
            'id', 'user', 'phone', 'date_of_birth', 'gender', 'gender_display',
            'goal', 'goal_display', 'weight_kg', 'height_cm', 'photo',
            'active_membership', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_active_membership(self, obj):
        membership = obj.memberships.filter(status='active').first()
        if membership:
            return {
                'id': membership.id,
                'plan': membership.get_plan_display(),
                'end_date': membership.end_date,
                'visits_left': membership.visits_left,
            }
        return None


class MemberProfileWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemberProfile
        fields = ['phone', 'date_of_birth', 'gender', 'goal', 'weight_kg', 'height_cm', 'photo']


# ──────────────────────────────────────────────
#  Membership
# ──────────────────────────────────────────────
class MembershipSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Membership
        fields = [
            'id', 'member', 'member_name', 'plan', 'plan_display',
            'status', 'status_display', 'start_date', 'end_date',
            'price_paid', 'visits_left', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_member_name(self, obj):
        return str(obj.member)


# ──────────────────────────────────────────────
#  TrainingClass
# ──────────────────────────────────────────────
class TrainingClassListSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    spots_available = serializers.ReadOnlyField()

    class Meta:
        model = TrainingClass
        fields = [
            'id', 'name', 'trainer', 'trainer_name', 'difficulty',
            'difficulty_display', 'capacity', 'spots_available',
            'duration_minutes', 'scheduled_at', 'room', 'price', 'is_cancelled',
        ]

    def get_trainer_name(self, obj):
        return str(obj.trainer) if obj.trainer else None


class TrainingClassDetailSerializer(serializers.ModelSerializer):
    trainer = TrainerListSerializer(read_only=True)
    trainer_id = serializers.PrimaryKeyRelatedField(
        queryset=Trainer.objects.all(), source='trainer', write_only=True,
        required=False, allow_null=True
    )
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    spots_available = serializers.ReadOnlyField()
    bookings_count = serializers.SerializerMethodField()

    class Meta:
        model = TrainingClass
        fields = [
            'id', 'name', 'description', 'trainer', 'trainer_id',
            'difficulty', 'difficulty_display', 'capacity', 'spots_available',
            'duration_minutes', 'scheduled_at', 'room', 'price',
            'is_cancelled', 'bookings_count', 'created_at',
        ]
        read_only_fields = ['created_at']

    def get_bookings_count(self, obj):
        return obj.bookings.filter(status='confirmed').count()


# ──────────────────────────────────────────────
#  Booking
# ──────────────────────────────────────────────
class BookingSerializer(serializers.ModelSerializer):
    member_name = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    class_scheduled_at = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'member', 'member_name', 'training_class', 'class_name',
            'class_scheduled_at', 'status', 'status_display',
            'booked_at', 'rating', 'review',
        ]
        read_only_fields = ['booked_at']

    def get_member_name(self, obj):
        return str(obj.member)

    def get_class_name(self, obj):
        return obj.training_class.name

    def get_class_scheduled_at(self, obj):
        return obj.training_class.scheduled_at

    def validate(self, attrs):
        training_class = attrs.get('training_class')
        if training_class and training_class.is_cancelled:
            raise serializers.ValidationError('Это занятие отменено.')
        if training_class and training_class.spots_available == 0:
            raise serializers.ValidationError('Нет свободных мест на это занятие.')
        return attrs


class BookingCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания записи (member определяется автоматически)."""
    class Meta:
        model = Booking
        fields = ['training_class', 'status', 'rating', 'review']

    def validate_training_class(self, value):
        if value.is_cancelled:
            raise serializers.ValidationError('Это занятие отменено.')
        if value.spots_available == 0:
            raise serializers.ValidationError('Нет свободных мест.')
        return value
