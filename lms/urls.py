from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView
from .views_subscription import SubscriptionAPIView  # Добавьте этот импорт

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
    path('subscriptions/', SubscriptionAPIView.as_view(), name='subscriptions'),
]