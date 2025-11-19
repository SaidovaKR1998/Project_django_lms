from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Course, Subscription  # Subscription теперь доступен
from .serializers import SubscriptionSerializer

class SubscriptionAPIView(APIView):
    """
    APIView для управления подписками на курсы
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Управление подпиской: добавление или удаление
        """
        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id обязателен"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем курс
        course = get_object_or_404(Course, id=course_id)

        # Проверяем существующую подписку
        subscription = Subscription.objects.filter(user=user, course=course)

        if subscription.exists():
            # Если подписка есть - удаляем ее
            subscription.delete()
            message = 'Подписка удалена'
            is_subscribed = False
        else:
            # Если подписки нет - создаем ее
            Subscription.objects.create(user=user, course=course)
            message = 'Подписка добавлена'
            is_subscribed = True

        return Response({
            "message": message,
            "is_subscribed": is_subscribed,
            "course_id": course_id,
            "course_title": course.title
        }, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Получение списка подписок пользователя
        """
        user = request.user
        subscriptions = Subscription.objects.filter(user=user)
        serializer = SubscriptionSerializer(subscriptions, many=True)

        return Response({
            "count": subscriptions.count(),
            "results": serializer.data
        }, status=status.HTTP_200_OK)
