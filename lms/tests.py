from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth.models import Group
from users.models import CustomUser
from .models import Course, Lesson, Subscription


class LessonTestCase(APITestCase):
    """
    Тесты для CRUD операций с уроками
    """

    def setUp(self):
        """
        Подготовка тестовых данных
        """
        # Создаем группы
        self.moderators_group, _ = Group.objects.get_or_create(name='moderators')

        # Создаем пользователей
        self.regular_user = CustomUser.objects.create_user(
            email='regular@example.com',
            password='testpass123',
            first_name='Regular',
            last_name='User'
        )

        self.moderator_user = CustomUser.objects.create_user(
            email='moderator@example.com',
            password='testpass123',
            first_name='Moderator',
            last_name='User'
        )
        self.moderator_user.groups.add(self.moderators_group)

        self.another_user = CustomUser.objects.create_user(
            email='another@example.com',
            password='testpass123',
            first_name='Another',
            last_name='User'
        )

        # Создаем курсы
        self.course_regular = Course.objects.create(
            title='Курс обычного пользователя',
            description='Описание курса',
            owner=self.regular_user
        )

        self.course_moderator = Course.objects.create(
            title='Курс модератора',
            description='Описание курса',
            owner=self.moderator_user
        )

        # Создаем уроки
        self.lesson_regular = Lesson.objects.create(
            title='Урок обычного пользователя',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=test123',
            course=self.course_regular,
            owner=self.regular_user
        )

        self.lesson_moderator = Lesson.objects.create(
            title='Урок модератора',
            description='Описание урока',
            video_link='https://www.youtube.com/watch?v=test456',
            course=self.course_moderator,
            owner=self.moderator_user
        )

    def test_lesson_list_authenticated(self):
        """
        Тест получения списка уроков авторизованным пользователем
        """
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(reverse('lesson-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Обычный пользователь должен видеть только свои уроки
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Урок обычного пользователя')

    def test_lesson_list_moderator(self):
        """
        Тест получения списка уроков модератором
        """
        self.client.force_authenticate(user=self.moderator_user)
        response = self.client.get(reverse('lesson-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Модератор должен видеть все уроки
        self.assertEqual(len(response.data['results']), 2)

    def test_lesson_create_regular_user(self):
        """
        Тест создания урока обычным пользователем
        """
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'title': 'Новый урок',
            'description': 'Описание нового урока',
            'video_link': 'https://www.youtube.com/watch?v=newlesson',
            'course': self.course_regular.id
        }

        response = self.client.post(reverse('lesson-list'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 3)
        self.assertEqual(response.data['title'], 'Новый урок')
        # Проверяем, что урок привязан к текущему пользователю
        self.assertEqual(Lesson.objects.get(title='Новый урок').owner, self.regular_user)

    def test_lesson_create_moderator_forbidden(self):
        """
        Тест запрета создания урока модератором
        """
        self.client.force_authenticate(user=self.moderator_user)

        data = {
            'title': 'Урок от модератора',
            'description': 'Описание урока',
            'video_link': 'https://www.youtube.com/watch?v=moderator',
            'course': self.course_moderator.id
        }

        response = self.client.post(reverse('lesson-list'), data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)  # Количество уроков не изменилось

    def test_lesson_update_owner(self):
        """
        Тест обновления урока владельцем
        """
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'title': 'Обновленный урок',
            'description': 'Обновленное описание',
            'video_link': 'https://www.youtube.com/watch?v=updated'
        }

        response = self.client.patch(
            reverse('lesson-detail', kwargs={'pk': self.lesson_regular.id}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson_regular.refresh_from_db()
        self.assertEqual(self.lesson_regular.title, 'Обновленный урок')

    def test_lesson_update_moderator(self):
        """
        Тест обновления урока модератором (чужого урока)
        """
        self.client.force_authenticate(user=self.moderator_user)

        data = {
            'title': 'Урок обновлен модератором',
            'description': 'Обновленное описание модератором'
        }

        response = self.client.patch(
            reverse('lesson-detail', kwargs={'pk': self.lesson_regular.id}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson_regular.refresh_from_db()
        self.assertEqual(self.lesson_regular.title, 'Урок обновлен модератором')

    def test_lesson_update_another_user_forbidden(self):
        """
        Тест запрета обновления урока другим пользователем
        """
        self.client.force_authenticate(user=self.another_user)

        data = {
            'title': 'Попытка обновить чужой урок',
            'description': 'Не должно работать'
        }

        response = self.client.patch(
            reverse('lesson-detail', kwargs={'pk': self.lesson_regular.id}),
            data
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_delete_owner(self):
        """
        Тест удаления урока владельцем
        """
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.delete(
            reverse('lesson-detail', kwargs={'pk': self.lesson_regular.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 1)  # Остался только урок модератора

    def test_lesson_delete_moderator_forbidden(self):
        """
        Тест запрета удаления урока модератором
        """
        self.client.force_authenticate(user=self.moderator_user)

        response = self.client.delete(
            reverse('lesson-detail', kwargs={'pk': self.lesson_regular.id})
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 2)  # Оба урока остались

    def test_lesson_youtube_validation(self):
        """
        Тест валидации YouTube ссылок
        """
        self.client.force_authenticate(user=self.regular_user)

        data = {
            'title': 'Урок с неправильной ссылкой',
            'description': 'Описание',
            'video_link': 'https://vimeo.com/123456',  # Не YouTube!
            'course': self.course_regular.id
        }

        response = self.client.post(reverse('lesson-list'), data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)


class SubscriptionTestCase(APITestCase):
    """
    Тесты для функционала подписок
    """

    def setUp(self):
        """
        Подготовка тестовых данных для подписок
        """
        self.user = CustomUser.objects.create_user(
            email='user@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        self.course = Course.objects.create(
            title='Тестовый курс',
            description='Описание курса',
            owner=self.user
        )

    def test_subscription_add(self):
        """
        Тест добавления подписки
        """
        self.client.force_authenticate(user=self.user)

        data = {'course_id': self.course.id}
        response = self.client.post(reverse('subscriptions'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка добавлена')
        self.assertTrue(response.data['is_subscribed'])
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_remove(self):
        """
        Тест удаления подписки
        """
        # Сначала создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)

        data = {'course_id': self.course.id}
        response = self.client.post(reverse('subscriptions'), data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Подписка удалена')
        self.assertFalse(response.data['is_subscribed'])
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscription_list(self):
        """
        Тест получения списка подписок
        """
        # Создаем несколько подписок
        course2 = Course.objects.create(title='Курс 2', description='Описание', owner=self.user)
        Subscription.objects.create(user=self.user, course=self.course)
        Subscription.objects.create(user=self.user, course=course2)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('subscriptions'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_subscription_course_field(self):
        """
        Тест наличия поля подписки в данных курса
        """
        # Создаем подписку
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('course-detail', kwargs={'pk': self.course.id}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_subscribed', response.data)
        self.assertTrue(response.data['is_subscribed'])


class PaginationTestCase(APITestCase):
    """
    Тесты пагинации
    """

    def setUp(self):
        """
        Создаем много уроков для тестирования пагинации
        """
        self.user = CustomUser.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )

        self.course = Course.objects.create(
            title='Курс для пагинации',
            description='Описание',
            owner=self.user
        )

        # Создаем 15 уроков
        for i in range(15):
            Lesson.objects.create(
                title=f'Урок {i + 1}',
                description=f'Описание урока {i + 1}',
                video_link='https://www.youtube.com/watch?v=test',
                course=self.course,
                owner=self.user
            )

    def test_pagination_default(self):
        """
        Тест пагинации по умолчанию (10 элементов)
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('lesson-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 10)  # По умолчанию 10 элементов
        self.assertIn('next', response.data)  # Должна быть следующая страница
        self.assertIn('count', response.data)
        self.assertEqual(response.data['count'], 15)

    def test_pagination_custom_page_size(self):
        """
        Тест пагинации с кастомным размером страницы
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('lesson-list') + '?page_size=5')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)  # Запросили 5 элементов

    def test_pagination_max_page_size(self):
        """
        Тест ограничения максимального размера страницы
        """
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('lesson-list') + '?page_size=100')  # Запрос больше максимума

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 15)  # Все элементы, но не больше максимума
