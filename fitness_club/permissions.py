from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrAdmin(BasePermission):
    """
    Разрешает доступ только владельцу объекта или администратору.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # Для MemberProfile
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Для Booking
        if hasattr(obj, 'member'):
            return obj.member.user == request.user
        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешает чтение всем аутентифицированным,
    запись — только администраторам.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff
