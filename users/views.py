from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import CustomUser, Payment
from .serializers import (
    UserRegisterSerializer, UserProfileSerializer, UserPublicSerializer,
    PaymentSerializer, UserProfileWithPaymentsSerializer, UserPrivateSerializer
)
from .permissions import IsProfileOwner


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserPublicSerializer  # По умолчанию для списка - публичная информация
    permission_classes = [IsAuthenticated]  # По умолчанию требуем авторизацию

    def get_serializer_class(self):
        """
        Выбор сериализатора в зависимости от действия и прав:
        - Регистрация: UserRegisterSerializer
        - Список пользователей: UserPublicSerializer (только публичная информация)
        - Просмотр своего профиля: UserProfileWithPaymentsSerializer (полная информация + платежи)
        - Просмотр чужого профиля: UserPublicSerializer (только публичная информация)
        - Редактирование: UserProfileSerializer
        """
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return UserProfileSerializer
        elif self.action == 'retrieve':
            # Проверяем, запрашивает ли пользователь свой профиль
            if self.get_object() == self.request.user:
                # Свой профиль - полная информация с платежами
                return UserProfileWithPaymentsSerializer
            else:
                # Чужой профиль - только публичная информация
                return UserPublicSerializer
        elif self.action == 'list':
            # Список пользователей - только публичная информация
            return UserPublicSerializer
        return UserPublicSerializer

    def get_permissions(self):
        """
        Настройка прав доступа:
        - Регистрация: доступна всем (AllowAny)
        - Просмотр списка: авторизованные пользователи
        - Просмотр деталей: авторизованные пользователи
        - Редактирование/удаление: только владелец профиля или админ
        """
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action == 'list':
            self.permission_classes = [IsAuthenticated]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsProfileOwner | IsAdminUser]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Получить профиль текущего пользователя (полная информация с платежами)"""
        serializer = UserProfileWithPaymentsSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated, IsProfileOwner])
    def update_profile(self, request):
        """Обновить профиль текущего пользователя"""
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с платежами
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        'paid_course',
        'paid_lesson',
        'payment_method'
    ]
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Немодераторы видят только свои платежи
        Модераторы и админы видят все платежи
        """
        user = self.request.user

        if user.is_staff or user.groups.filter(name='moderators').exists():
            return Payment.objects.all()
        else:
            return Payment.objects.filter(user=user)
