from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonListCreateAPIView, LessonRetrieveUpdateDestroyAPIView
from .views_subscription import SubscriptionAPIView  # Добавьте этот импорт
from .views_payment import (
    CreateStripePaymentSessionAPIView,
    CheckPaymentStatusAPIView,
    PaymentSuccessAPIView,
    PaymentCancelAPIView
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')

urlpatterns = [
    path('', include(router.urls)),
    path('lessons/', LessonListCreateAPIView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonRetrieveUpdateDestroyAPIView.as_view(), name='lesson-detail'),
    path('subscriptions/', SubscriptionAPIView.as_view(), name='subscriptions'),

    # Stripe платежи
    path('payments/create-session/', CreateStripePaymentSessionAPIView.as_view(), name='create-payment-session'),
    path('payments/<int:payment_id>/status/', CheckPaymentStatusAPIView.as_view(), name='check-payment-status'),
    path('payments/<int:payment_id>/success/', PaymentSuccessAPIView.as_view(), name='payment-success'),
    path('payments/<int:payment_id>/cancel/', PaymentCancelAPIView.as_view(), name='payment-cancel'),
]