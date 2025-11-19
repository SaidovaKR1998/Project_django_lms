from django.db import models
from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re
from users.models import CustomUser


# Выносим валидатор прямо в models.py чтобы избежать циклического импорта
def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на YouTube
    """
    if value is None or value == '':
        return

    # Парсим URL
    parsed_url = urlparse(value)

    # Проверяем домен
    allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

    if parsed_url.netloc not in allowed_domains:
        raise ValidationError(
            f'Ссылка должна вести на YouTube. Получен домен: {parsed_url.netloc}'
        )

    # Дополнительная проверка с помощью регулярного выражения
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    if not re.match(youtube_pattern, value):
        raise ValidationError('Некорректная ссылка на YouTube')


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', blank=True, null=True, verbose_name='Превью')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    preview = models.ImageField(upload_to='lessons/previews/', blank=True, null=True, verbose_name='Превью')
    video_link = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на видео',
        validators=[validate_youtube_url]
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name='Курс')
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Владелец')

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['id']

    def __str__(self):
        return self.title


class Subscription(models.Model):
    """
    Модель подписки пользователя на обновления курса
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='subscriptions'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс',
        related_name='subscriptions'
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ['user', 'course']  # Одна подписка на курс для пользователя

    def __str__(self):
        return f"{self.user.email} подписан на {self.course.title}"