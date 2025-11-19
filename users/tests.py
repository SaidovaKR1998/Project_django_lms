from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Payment
from lms.models import Course, Lesson


class UserTestCase(APITestCase):
    """
    Тесты для функционала пользователей
    """

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        self.user1 = CustomUser.objects.create_user(
            email='user1@example.com',
            password='testpass123',
            first_name='User1',
            last_name='Test'
        )

        self.user2 = CustomUser.objects.create_user(
            email='user2@example.com',
            password='testpass123',
            first_name='User2',
            last_name='Test'
        )

        self.admin_user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )

    def test_user_registration(self):
        """
        Тест регистрации пользователя
        """
        data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(reverse('customuser-list'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 4)  # 3 существующих + 1 новый
        self.assertEqual(response.data['email'], 'newuser@example.com')
        self.assertNotIn('password', response.data)  # Пароль не должен возвращаться

    def test_user_registration_password_mismatch(self):
        """
        Тест регистрации с несовпадающими паролями
        """
        data = {
            'email': 'newuser@example.com',
            'password': 'pass123',
            'password2': 'differentpass',
            'first_name': 'New',
            'last_name': 'User'
        }

        response = self.client.post(reverse('customuser-list'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_user_profile_retrieve_own(self):
        """
        Тест получения своего профиля
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('customuser-detail', kwargs={'pk': self.user1.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user1@example.com')
        self.assertEqual(response.data['first_name'], 'User1')
        self.assertEqual(response.data['last_name'], 'Test')

    def test_user_profile_retrieve_other(self):
        """
        Тест получения чужого профиля (только публичная информация)
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('customuser-detail', kwargs={'pk': self.user2.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user2@example.com')
        self.assertEqual(response.data['first_name'], 'User2')
        self.assertNotIn('last_name', response.data)  # Фамилия не должна быть в публичном профиле

    def test_user_profile_update_own(self):
        """
        Тест обновления своего профиля
        """
        self.client.force_authenticate(user=self.user1)

        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }

        response = self.client.patch(
            reverse('customuser-detail', kwargs={'pk': self.user1.id}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated')

    def test_user_profile_update_other_forbidden(self):
        """
        Тест запрета обновления чужого профиля
        """
        self.client.force_authenticate(user=self.user1)

        data = {
            'first_name': 'Hacked',
            'last_name': 'User'
        }

        response = self.client.patch(
            reverse('customuser-detail', kwargs={'pk': self.user2.id}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_profile_endpoint(self):
        """
        Тест эндпоинта /profile/
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('customuser-profile'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user1@example.com')
        self.assertIn('payments', response.data)  # Должна быть история платежей


class PaymentTestCase(APITestCase):
    """
    Тесты для платежей
    """

    def setUp(self):
        """
        Подготовка тестовых данных для платежей
        """
        self.user1 = CustomUser.objects.create_user(
            email='user1@example.com',
            password='testpass123'
        )

        self.user2 = CustomUser.objects.create_user(
            email='user2@example.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Курс для платежей',
            description='Описание',
            owner=self.user1
        )

        self.lesson = Lesson.objects.create(
            title='Урок для платежей',
            description='Описание',
            video_link='https://www.youtube.com/watch?v=test',
            course=self.course,
            owner=self.user1
        )

        # Создаем платежи
        self.payment1 = Payment.objects.create(
            user=self.user1,
            paid_course=self.course,
            amount=10000.00,
            payment_method='transfer'
        )

        self.payment2 = Payment.objects.create(
            user=self.user2,
            paid_lesson=self.lesson,
            amount=2000.00,
            payment_method='cash'
        )

    def test_payment_list_own(self):
        """
        Тест получения списка своих платежей
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('payment-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # Только свои платежи
        self.assertEqual(response.data['results'][0]['id'], self.payment1.id)

    def test_payment_filter_by_course(self):
        """
        Тест фильтрации платежей по курсу
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('payment-list') + f'?paid_course={self.course.id}')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['paid_course'], self.course.id)

    def test_payment_ordering(self):
        """
        Тест сортировки платежей
        """
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(reverse('payment-list') + '?ordering=payment_date')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
