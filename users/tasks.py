from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

User = get_user_model()


@shared_task
def check_inactive_users():
    """
    Периодическая задача для блокировки пользователей, не заходивших более месяца
    """
    try:
        # Дата месяц назад
        month_ago = timezone.now() - timedelta(days=30)

        # Находим пользователей, которые не заходили более месяца и еще активны
        inactive_users = User.objects.filter(
            last_login__lt=month_ago,
            is_active=True
        )

        count_before = inactive_users.count()

        # Блокируем пользователей и отправляем уведомления
        for user in inactive_users:
            user.is_active = False
            user.save(update_fields=['is_active'])

            # Асинхронная отправка уведомления о блокировке
            send_user_blocked_notification.delay(user.id)

        return f"Blocked {count_before} inactive users and sent notifications"

    except Exception as e:
        return f"Error checking inactive users: {str(e)}"


@shared_task
def send_user_blocked_notification(user_id):
    """
    Задача для отправки уведомления о блокировке пользователя
    """
    try:
        user = User.objects.get(id=user_id)

        subject = 'Ваш аккаунт был временно заблокирован'

        # Отправляем email
        send_mail(
            subject=subject,
            message=f'''Здравствуйте, {user.first_name}!

Ваш аккаунт был временно заблокирован из-за длительного отсутствия активности (более 30 дней).

Для разблокировки аккаунта обратитесь в службу поддержки.

С уважением,
Команда LMS Platform''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        return f"Sent blocked notification to {user.email}"

    except User.DoesNotExist:
        return f"User with id {user_id} does not exist"
    except Exception as e:
        return f"Error sending blocked notification: {str(e)}"