from rest_framework import permissions


class IsProfileOwner(permissions.BasePermission):
    """
    Разрешает редактирование только своего профиля
    """

    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True

        # Запись разрешена только владельцу профиля
        return obj == request.user
