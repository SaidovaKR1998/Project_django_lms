from django.contrib import admin
from .models import Course, Lesson, Subscription  # Добавьте Subscription


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 1
    readonly_fields = ['subscribed_at']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'lessons_count')
    search_fields = ('title',)
    inlines = [LessonInline, SubscriptionInline]  # Добавьте SubscriptionInline

    def lessons_count(self, obj):
        return obj.lessons.count()

    lessons_count.short_description = 'Количество уроков'


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'owner')
    list_filter = ('course',)
    search_fields = ('title', 'description')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'subscribed_at')
    list_filter = ('subscribed_at', 'course')
    search_fields = ('user__email', 'course__title')
    readonly_fields = ['subscribed_at']

