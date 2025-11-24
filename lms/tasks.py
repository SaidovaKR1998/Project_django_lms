from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Course, Subscription


@shared_task
def send_course_update_notification(course_id):
    """
    Асинхронная задача для отправки уведомлений об обновлении курса
    """
    try:
        course = Course.objects.get(id=course_id)
        subscriptions = Subscription.objects.filter(course=course)

        if not subscriptions.exists():
            return f"No subscribers for course {course.title}"

        subject = f'Обновление курса: {course.title}'

        for subscription in subscriptions:
            user = subscription.user

            # Формируем HTML сообщение
            html_message = render_to_string('emails/course_update.html', {
                'user': user,
                'course': course,
            })

            # Отправляем email
            send_mail(
                subject=subject,
                message=f'Курс "{course.title}" был обновлен. Проверьте новые материалы!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

        return f"Sent update notifications to {subscriptions.count()} subscribers for course {course.title}"

    except Course.DoesNotExist:
        return f"Course with id {course_id} does not exist"
    except Exception as e:
        return f"Error sending notifications: {str(e)}"
