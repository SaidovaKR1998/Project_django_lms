from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    help = 'Создает группы пользователей'

    def handle(self, *args, **options):
        # Создаем группу модераторов
        moderators_group, created = Group.objects.get_or_create(name='moderators')

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа модераторов создана')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Группа модераторов уже существует')
            )

        # Можно добавить права для группы
        # Например, права на просмотр и изменение курсов и уроков
        course_permissions = Permission.objects.filter(
            content_type__app_label='lms',
            content_type__model__in=['course', 'lesson']
        )

        # Добавляем права на просмотр и изменение (но не создание и удаление)
        for perm in course_permissions:
            if 'view' in perm.codename or 'change' in perm.codename:
                moderators_group.permissions.add(perm)

        self.stdout.write(
            self.style.SUCCESS('Группы созданы и настроены')
        )
