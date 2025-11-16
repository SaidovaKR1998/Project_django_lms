from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsModerator(BasePermission):
    """
    Права доступа для модераторов
    """
    def has_permission(self, request, view):
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
        if request.user.groups.filter(name='moderators').exists():
            return True
        return obj.owner == request.user

class IsNotModerator(BasePermission):
    """
    Запрещает доступ модераторам (для создания/удаления)
    """
    def has_permission(self, request, view):
        return not request.user.groups.filter(name='moderators').exists()
