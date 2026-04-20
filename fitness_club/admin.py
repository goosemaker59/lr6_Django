from django.contrib import admin
from django.utils.html import format_html
from .models import Trainer, MemberProfile, Membership, TrainingClass, Booking


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialization', 'experience_years', 'hourly_rate', 'is_active', 'preview_photo']
    list_filter = ['specialization', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    list_editable = ['is_active']
    ordering = ['user__last_name']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Тренер'

    def preview_photo(self, obj):
        if obj.photo:
            return format_html('<img src="{}" height="40" style="border-radius:4px"/>', obj.photo.url)
        return '—'
    preview_photo.short_description = 'Фото'


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'get_full_name', 'phone', 'gender', 'goal', 'created_at']
    list_filter = ['gender', 'goal']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Имя'


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'status', 'start_date', 'end_date', 'price_paid', 'visits_left']
    list_filter = ['plan', 'status']
    search_fields = ['member__user__first_name', 'member__user__last_name']
    ordering = ['-start_date']


class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    readonly_fields = ['booked_at']


@admin.register(TrainingClass)
class TrainingClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'trainer', 'difficulty', 'scheduled_at', 'capacity', 'spots_available', 'price', 'is_cancelled']
    list_filter = ['difficulty', 'is_cancelled', 'trainer']
    search_fields = ['name', 'description', 'room']
    ordering = ['scheduled_at']
    inlines = [BookingInline]

    def spots_available(self, obj):
        return obj.spots_available
    spots_available.short_description = 'Свободных мест'


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['member', 'training_class', 'status', 'booked_at', 'rating']
    list_filter = ['status']
    search_fields = ['member__user__first_name', 'member__user__last_name', 'training_class__name']
    ordering = ['-booked_at']
    readonly_fields = ['booked_at']
