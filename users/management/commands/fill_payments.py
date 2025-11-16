from django.core.management.base import BaseCommand
from users.models import CustomUser, Payment
from lms.models import Course, Lesson
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми платежами'

    def handle(self, *args, **options):
        # Очищаем существующие платежи
        Payment.objects.all().delete()

        # Получаем пользователей, курсы и уроки
        users = CustomUser.objects.all()
        courses = Course.objects.all()
        lessons = Lesson.objects.all()

        # Если нет данных, создаем тестовые
        if not users.exists():
            user1 = CustomUser.objects.create_user(
                email='user1@example.com',
                password='password123',
                first_name='User1'
            )
            user2 = CustomUser.objects.create_user(
                email='user2@example.com',
                password='password123',
                first_name='User2'
            )
            users = [user1, user2]
            self.stdout.write('Созданы тестовые пользователи')
        else:
            users = list(users[:2])  # Берем первых двух пользователей

        if not courses.exists():
            course1 = Course.objects.create(
                title='Python Basics',
                description='Основы Python'
            )
            course2 = Course.objects.create(
                title='Django Web Development',
                description='Разработка на Django'
            )
            courses = [course1, course2]
            self.stdout.write('Созданы тестовые курсы')
        else:
            courses = list(courses[:2])  # Берем первые два курса

        if not lessons.exists() and courses:
            lesson1 = Lesson.objects.create(
                title='Введение в Python',
                description='Первое знакомство',
                course=courses[0]
            )
            lesson2 = Lesson.objects.create(
                title='Установка Django',
                description='Настройка окружения',
                course=courses[1]
            )
            lessons = [lesson1, lesson2]
            self.stdout.write('Созданы тестовые уроки')
        else:
            lessons = list(lessons[:2])  # Берем первые два урока

        # Создаем тестовые платежи
        payments_data = [
            # Платежи за курсы
            {
                'user': users[0],
                'paid_course': courses[0],
                'paid_lesson': None,
                'amount': 10000.00,
                'payment_method': 'transfer'
            },
            {
                'user': users[1],
                'paid_course': courses[1],
                'paid_lesson': None,
                'amount': 15000.00,
                'payment_method': 'cash'
            },
            {
                'user': users[0],
                'paid_course': courses[1],
                'paid_lesson': None,
                'amount': 15000.00,
                'payment_method': 'transfer'
            },
            # Платежи за уроки
            {
                'user': users[1],
                'paid_course': None,
                'paid_lesson': lessons[0],
                'amount': 2000.00,
                'payment_method': 'cash'
            },
            {
                'user': users[0],
                'paid_course': None,
                'paid_lesson': lessons[1],
                'amount': 2500.00,
                'payment_method': 'transfer'
            },
        ]

        created_count = 0
        for payment_data in payments_data:
            try:
                payment = Payment.objects.create(
                    user=payment_data['user'],
                    paid_course=payment_data['paid_course'],
                    paid_lesson=payment_data['paid_lesson'],
                    amount=payment_data['amount'],
                    payment_method=payment_data['payment_method']
                )
                # Устанавливаем кастомную дату (прошлые даты)
                days_ago = random.randint(1, 30)
                payment.payment_date = datetime.now() - timedelta(days=days_ago)
                payment.save()
                created_count += 1
                self.stdout.write(f'Создан платеж: {payment}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка при создании платежа: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Успешно создано {created_count} тестовых платежей')
        )