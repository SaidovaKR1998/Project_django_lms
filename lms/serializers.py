from rest_framework import serializers
from .models import Course, Lesson, Subscription  # Теперь Subscription доступен


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Lesson
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'user', 'course', 'subscribed_at']
        read_only_fields = ['user', 'subscribed_at']


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_lessons_count(self, obj):
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        # Признак подписки текущего пользователя на курс
        user = self.context['request'].user
        if user.is_authenticated:
            return obj.subscriptions.filter(user=user).exists()
        return False
