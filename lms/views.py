from rest_framework import viewsets, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsOwner, IsOwnerOrModerator, IsNotModerator
from .paginators import LessonCoursePagination
from .tasks import send_course_update_notification

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['owner']
    pagination_class = LessonCoursePagination

    def get_permissions(self):
        """
        Настройка прав доступа для курсов:
        - Создание: только не-модераторы
        - Просмотр списка и деталей: авторизованные пользователи (видят только свои + модераторы видят все)
        - Обновление: владелец или модератор
        - Удаление: только владелец
        """
        if self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        elif self.action in ['update', 'partial_update']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, IsOwner]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Немодераторы видят только свои курсы
        Модераторы видят все курсы
        """
        user = self.request.user

        if user.groups.filter(name='moderators').exists() or user.is_staff:
            # Модераторы и админы видят все курсы
            return Course.objects.all()
        else:
            # Обычные пользователи видят только свои курсы
            return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        """Автоматически привязываем курс к текущему пользователю"""
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        """
        Сохранение обновленного курса и отправка уведомлений подписчикам
        """
        instance = serializer.save()

        # Асинхронная отправка уведомлений подписчикам
        send_course_update_notification.delay(instance.id)

        return instance


class LessonListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['course', 'owner']
    pagination_class = LessonCoursePagination

    def get_queryset(self):
        """
        Немодераторы видят только свои уроки
        Модераторы видят все уроки
        """
        user = self.request.user

        if user.groups.filter(name='moderators').exists() or user.is_staff:
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        """
        Создание уроков разрешено только не-модераторам
        Просмотр списка - всем авторизованным
        """
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsNotModerator]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматически привязываем урок к текущему пользователю"""
        serializer.save(owner=self.request.user)


class LessonRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]

    def get_permissions(self):
        """
        Обновление: владелец или модератор
        Удаление: только владелец
        Просмотр: авторизованные (с фильтрацией через get_queryset)
        """
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrModerator]
        elif self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Немодераторы видят только свои уроки
        Модераторы видят все уроки
        """
        user = self.request.user

        if user.groups.filter(name='moderators').exists() or user.is_staff:
            return Lesson.objects.all()
        else:
            return Lesson.objects.filter(owner=user)
