from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # Добавьте эти строки для решения конфликта
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.email


# ДОБАВЬТЕ ЭТУ МОДЕЛЬ Payment В КОНЕЦ ФАЙЛА
class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Наличные'),
        ('transfer', 'Перевод на счет'),
        ('stripe', 'Stripe'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('canceled', 'Отменено'),
    ]

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='payments'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    paid_course = models.ForeignKey(
        'lms.Course',
        on_delete=models.CASCADE,
        verbose_name='Оплаченный курс',
        null=True,
        blank=True,
        related_name='payments'
    )
    paid_lesson = models.ForeignKey(
        'lms.Lesson',
        on_delete=models.CASCADE,
        verbose_name='Оплаченный урок',
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты',
        default='transfer'
    )
    # Новые поля для Stripe
    stripe_product_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID продукта в Stripe'
    )
    stripe_price_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID цены в Stripe'
    )
    stripe_session_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='ID сессии в Stripe'
    )
    stripe_payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на оплату Stripe'
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='Статус оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        course_title = self.paid_course.title if self.paid_course else None
        lesson_title = self.paid_lesson.title if self.paid_lesson else None

        if course_title:
            return f"{self.user.email} - {course_title} - {self.amount} - {self.payment_status}"
        elif lesson_title:
            return f"{self.user.email} - {lesson_title} - {self.amount} - {self.payment_status}"
        return f"{self.user.email} - {self.amount} - {self.payment_status}"


    # Используем вашу кастомную модель пользователя
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='payments'
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата оплаты'
    )
    paid_course = models.ForeignKey(
        'lms.Course',  # Строковая ссылка
        on_delete=models.CASCADE,
        verbose_name='Оплаченный курс',
        null=True,
        blank=True,
        related_name='payments'
    )
    paid_lesson = models.ForeignKey(
        'lms.Lesson',  # Строковая ссылка
        on_delete=models.CASCADE,
        verbose_name='Оплаченный урок',
        null=True,
        blank=True,
        related_name='payments'
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Сумма оплаты'
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name='Способ оплаты'
    )

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-payment_date']

    def __str__(self):
        # Используем безопасные обращения к атрибутам
        course_title = self.paid_course.title if self.paid_course else None
        lesson_title = self.paid_lesson.title if self.paid_lesson else None

        if course_title:
            return f"{self.user.email} - {course_title} - {self.amount}"
        elif lesson_title:
            return f"{self.user.email} - {lesson_title} - {self.amount}"
        return f"{self.user.email} - {self.amount}"