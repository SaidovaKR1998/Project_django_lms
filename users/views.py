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
from lms.paginators import LessonCoursePagination  # Добавьте этот импорт


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
    pagination_class = LessonCoursePagination  # Добавьте пагинацию

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