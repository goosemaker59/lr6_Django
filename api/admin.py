from django.contrib import admin
from .models import Trainer, Member, Membership


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'specialization', 'experience_years', 'phone', 'created_at']
    list_filter = ['specialization', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'specialization', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone', 'date_of_birth', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'member', 'membership_type', 'status', 'start_date', 'end_date', 'price', 'trainer']
    list_filter = ['membership_type', 'status', 'start_date', 'end_date']
    search_fields = ['member__user__username', 'member__user__first_name', 'member__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
