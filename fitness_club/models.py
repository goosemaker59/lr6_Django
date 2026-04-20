from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# ──────────────────────────────────────────────
#  Table 1: Trainer
# ──────────────────────────────────────────────
class Trainer(models.Model):
    """Тренер фитнес-клуба."""

    SPECIALIZATION_CHOICES = [
        ('yoga', 'Йога'),
        ('crossfit', 'Кроссфит'),
        ('pilates', 'Пилатес'),
        ('boxing', 'Бокс'),
        ('swimming', 'Плавание'),
        ('strength', 'Силовые тренировки'),
        ('cardio', 'Кардио'),
        ('stretching', 'Растяжка'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='trainer_profile',
        verbose_name='Пользователь'
    )
    specialization = models.CharField(
        max_length=50,
        choices=SPECIALIZATION_CHOICES,
        verbose_name='Специализация'
    )
    bio = models.TextField(blank=True, verbose_name='О себе')
    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name='Опыт (лет)'
    )
    photo = models.ImageField(
        upload_to='trainers/', null=True, blank=True,
        verbose_name='Фото'
    )
    hourly_rate = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        verbose_name='Ставка в час (руб.)'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
        ordering = ['user__last_name']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_specialization_display()})"


# ──────────────────────────────────────────────
#  Table 2: MemberProfile
# ──────────────────────────────────────────────
class MemberProfile(models.Model):
    """Профиль члена клуба."""

    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
        ('O', 'Другой'),
    ]

    GOAL_CHOICES = [
        ('weight_loss', 'Похудение'),
        ('muscle_gain', 'Набор массы'),
        ('endurance', 'Выносливость'),
        ('flexibility', 'Гибкость'),
        ('health', 'Здоровье'),
        ('sport', 'Спортивные достижения'),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name='member_profile',
        verbose_name='Пользователь'
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Дата рождения')
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES,
        blank=True, verbose_name='Пол'
    )
    goal = models.CharField(
        max_length=20, choices=GOAL_CHOICES,
        blank=True, verbose_name='Цель'
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1,
        null=True, blank=True,
        verbose_name='Вес (кг)'
    )
    height_cm = models.PositiveIntegerField(
        null=True, blank=True,
        verbose_name='Рост (см)'
    )
    photo = models.ImageField(
        upload_to='members/', null=True, blank=True,
        verbose_name='Фото'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Профиль участника'
        verbose_name_plural = 'Профили участников'
        ordering = ['-created_at']

    def __str__(self):
        return f"Профиль: {self.user.get_full_name() or self.user.username}"


# ──────────────────────────────────────────────
#  Table 3: Membership (абонемент)
# ──────────────────────────────────────────────
class Membership(models.Model):
    """Абонемент / подписка члена клуба."""

    PLAN_CHOICES = [
        ('trial', 'Пробный (1 неделя)'),
        ('basic', 'Базовый (1 месяц)'),
        ('standard', 'Стандарт (3 месяца)'),
        ('premium', 'Премиум (6 месяцев)'),
        ('annual', 'Годовой (12 месяцев)'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('expired', 'Истёк'),
        ('frozen', 'Заморожен'),
        ('cancelled', 'Отменён'),
    ]

    member = models.ForeignKey(
        MemberProfile, on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Участник'
    )
    plan = models.CharField(
        max_length=20, choices=PLAN_CHOICES,
        verbose_name='Тариф'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='active', verbose_name='Статус'
    )
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    price_paid = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name='Оплачено (руб.)'
    )
    visits_left = models.IntegerField(
        null=True, blank=True,
        verbose_name='Осталось посещений (null = безлимит)'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.member} — {self.get_plan_display()} [{self.get_status_display()}]"


# ──────────────────────────────────────────────
#  Table 4: TrainingClass (групповое занятие)
# ──────────────────────────────────────────────
class TrainingClass(models.Model):
    """Групповое занятие / тренировка."""

    DIFFICULTY_CHOICES = [
        (1, 'Начальный'),
        (2, 'Лёгкий'),
        (3, 'Средний'),
        (4, 'Продвинутый'),
        (5, 'Экспертный'),
    ]

    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    trainer = models.ForeignKey(
        Trainer, on_delete=models.SET_NULL,
        null=True, related_name='classes',
        verbose_name='Тренер'
    )
    difficulty = models.IntegerField(
        choices=DIFFICULTY_CHOICES,
        default=3, verbose_name='Уровень сложности'
    )
    capacity = models.PositiveIntegerField(
        default=20, verbose_name='Макс. участников'
    )
    duration_minutes = models.PositiveIntegerField(
        default=60, verbose_name='Длительность (мин)'
    )
    scheduled_at = models.DateTimeField(verbose_name='Дата и время занятия')
    room = models.CharField(max_length=50, blank=True, verbose_name='Зал / помещение')
    price = models.DecimalField(
        max_digits=8, decimal_places=2,
        default=0, verbose_name='Цена (руб., 0 = включено в абонемент)'
    )
    is_cancelled = models.BooleanField(default=False, verbose_name='Отменено')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Занятие'
        verbose_name_plural = 'Занятия'
        ordering = ['scheduled_at']

    def __str__(self):
        return f"{self.name} — {self.scheduled_at.strftime('%d.%m.%Y %H:%M')}"

    @property
    def spots_available(self):
        booked = self.bookings.filter(status='confirmed').count()
        return max(0, self.capacity - booked)


# ──────────────────────────────────────────────
#  Table 5: Booking (запись на занятие)
# ──────────────────────────────────────────────
class Booking(models.Model):
    """Запись участника на групповое занятие."""

    STATUS_CHOICES = [
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('attended', 'Посещено'),
        ('no_show', 'Не явился'),
    ]

    member = models.ForeignKey(
        MemberProfile, on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Участник'
    )
    training_class = models.ForeignKey(
        TrainingClass, on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='Занятие'
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='confirmed', verbose_name='Статус'
    )
    booked_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка (1-5)'
    )
    review = models.TextField(blank=True, verbose_name='Отзыв')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи на занятия'
        ordering = ['-booked_at']
        # Один участник не может записаться дважды на одно занятие
        unique_together = [['member', 'training_class']]

    def __str__(self):
        return f"{self.member} → {self.training_class} [{self.get_status_display()}]"
