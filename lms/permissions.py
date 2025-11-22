from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsProfileOwner(BasePermission):
    """
    Права доступа для владельцев профиля
    """
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True
        # Запись разрешена только владельцу профиля
        return obj == request.user

class IsModerator(BasePermission):
    """
    Права доступа для модераторов
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moderators').exists()

    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name='moderators').exists()

class IsOwner(BasePermission):
    """
    Права доступа для владельцев объектов
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class IsOwnerOrModerator(BasePermission):
    """
    Права доступа для владельцев или модераторов
    """
    def has_object_permission(self, request, view, obj):
        # Модераторы имеют доступ ко всем объектам (кроме удаления)
        if request.user.groups.filter(name='moderators').exists():
            return True
        # Владельцы имеют доступ к своим объектам
        return obj.owner == request.user

class IsNotModerator(BasePermission):
    """
    Запрещает доступ модераторам (для создания/удаления)
    """
    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()

class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает чтение всем, а запись только владельцам
    """
    def has_object_permission(self, request, view, obj):
        # Чтение разрешено для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True
        # Запись разрешена только владельцу
        return obj.owner == request.user
