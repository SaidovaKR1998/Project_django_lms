from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from .models import CustomUser, Payment
from .serializers import UserRegisterSerializer, UserProfileSerializer, UserPublicSerializer, PaymentSerializer, \
    UserProfileWithPaymentsSerializer
from .permissions import IsProfileOwner


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        elif self.action in ['update', 'partial_update']:
            return UserProfileSerializer
        elif self.action == 'retrieve':
            if self.get_object() == self.request.user:
                # Для своего профиля - с историей платежей
                return UserProfileWithPaymentsSerializer
            else:
                return UserPublicSerializer
        return UserPublicSerializer

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsProfileOwner]
        return [permission() for permission in self.permission_classes]

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Получить профиль текущего пользователя"""
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
    ordering = ['-payment_date']  # Сортировка по умолчанию - новые сначала

    def get_queryset(self):
        """
        Пользователи видят только свои платежи
        Модераторы видят все платежи
        """
        user = self.request.user

        if user.is_staff or user.groups.filter(name='moderators').exists():
            # Модераторы и админы видят все платежи
            return Payment.objects.all()
        else:
            # Обычные пользователи видят только свои платежи
            return Payment.objects.filter(user=user)
