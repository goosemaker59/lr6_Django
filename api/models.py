from django.db import models
from django.contrib.auth.models import User


class Trainer(models.Model):
    """Модель тренера"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trainer_profile')
    specialization = models.CharField(max_length=200, verbose_name='Специализация')
    experience_years = models.IntegerField(verbose_name='Опыт работы (лет)')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    bio = models.TextField(blank=True, null=True, verbose_name='Биография')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.specialization}"


class Member(models.Model):
    """Модель участника клуба"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='member_profile')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    address = models.TextField(blank=True, null=True, verbose_name='Адрес')
    emergency_contact = models.CharField(max_length=200, blank=True, null=True, verbose_name='Контакт для экстренной связи')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"


class Membership(models.Model):
    """Модель абонемента"""
    MEMBERSHIP_TYPES = [
        ('basic', 'Базовый'),
        ('premium', 'Премиум'),
        ('vip', 'VIP'),
    ]

    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('expired', 'Истек'),
        ('suspended', 'Приостановлен'),
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='memberships', verbose_name='Участник')
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_TYPES, verbose_name='Тип абонемента')
    start_date = models.DateField(verbose_name='Дата начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name='Статус')
    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='memberships',
        verbose_name='Персональный тренер'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Абонемент'
        verbose_name_plural = 'Абонементы'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.member} - {self.get_membership_type_display()} ({self.status})"
