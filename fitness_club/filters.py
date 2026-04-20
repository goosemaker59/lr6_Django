import django_filters
from django.utils import timezone
from .models import TrainingClass, Booking, Membership


class TrainingClassFilter(django_filters.FilterSet):
    """Расширенные фильтры для занятий."""
    scheduled_after = django_filters.DateTimeFilter(
        field_name='scheduled_at', lookup_expr='gte',
        label='Занятия после даты (ISO 8601)'
    )
    scheduled_before = django_filters.DateTimeFilter(
        field_name='scheduled_at', lookup_expr='lte',
        label='Занятия до даты (ISO 8601)'
    )
    upcoming = django_filters.BooleanFilter(
        method='filter_upcoming',
        label='Только предстоящие занятия'
    )
    price_max = django_filters.NumberFilter(
        field_name='price', lookup_expr='lte',
        label='Цена не выше'
    )
    has_spots = django_filters.BooleanFilter(
        method='filter_has_spots',
        label='Только с доступными местами'
    )

    class Meta:
        model = TrainingClass
        fields = ['trainer', 'difficulty', 'is_cancelled']

    def filter_upcoming(self, queryset, name, value):
        if value:
            return queryset.filter(scheduled_at__gte=timezone.now(), is_cancelled=False)
        return queryset

    def filter_has_spots(self, queryset, name, value):
        if value:
            from django.db.models import Count, F, Q
            return queryset.annotate(
                confirmed_count=Count(
                    'bookings',
                    filter=Q(bookings__status='confirmed')
                )
            ).filter(confirmed_count__lt=F('capacity'))
        return queryset


class BookingFilter(django_filters.FilterSet):
    booked_after = django_filters.DateTimeFilter(
        field_name='booked_at', lookup_expr='gte'
    )
    booked_before = django_filters.DateTimeFilter(
        field_name='booked_at', lookup_expr='lte'
    )

    class Meta:
        model = Booking
        fields = ['status', 'training_class', 'member', 'rating']


class MembershipFilter(django_filters.FilterSet):
    active_now = django_filters.BooleanFilter(
        method='filter_active_now',
        label='Только активные сейчас'
    )

    class Meta:
        model = Membership
        fields = ['plan', 'status', 'member']

    def filter_active_now(self, queryset, name, value):
        if value:
            today = timezone.now().date()
            return queryset.filter(
                status='active',
                start_date__lte=today,
                end_date__gte=today
            )
        return queryset
