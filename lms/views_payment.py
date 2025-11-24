from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.conf import settings
from .models import Course, Lesson
from users.models import Payment
from .services import StripeService
import stripe


class CreateStripePaymentSessionAPIView(APIView):
    """
    API для создания сессии оплаты через Stripe
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Создание платежной сессии для курса или урока
        """
        user = request.user
        course_id = request.data.get('course_id')
        lesson_id = request.data.get('lesson_id')

        if not course_id and not lesson_id:
            return Response(
                {"error": "Необходимо указать course_id или lesson_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Получаем объект курса или урока
        if course_id:
            item = get_object_or_404(Course, id=course_id)
            item_type = 'course'
            item_name = item.title
            item_description = f"Курс: {item.title}"
        else:
            item = get_object_or_404(Lesson, id=lesson_id)
            item_type = 'lesson'
            item_name = item.title
            item_description = f"Урок: {item.title} (Курс: {item.course.title})"

        # Создаем платеж в нашей системе
        payment = Payment.objects.create(
            user=user,
            paid_course=item if item_type == 'course' else None,
            paid_lesson=item if item_type == 'lesson' else None,
            amount=100.00,  # Фиксированная цена для примера
            payment_method='stripe',
            payment_status='pending'
        )

        try:
            # Создаем продукт в Stripe
            product = StripeService.create_product(
                name=item_name,
                description=item_description
            )

            # Создаем цену в Stripe
            price = StripeService.create_price(
                product_id=product.id,
                amount=float(payment.amount)  # Конвертируем Decimal в float
            )

            # Создаем URL для перенаправления
            success_url = request.build_absolute_uri(
                reverse('payment-success', kwargs={'payment_id': payment.id})
            )
            cancel_url = request.build_absolute_uri(
                reverse('payment-cancel', kwargs={'payment_id': payment.id})
            )

            # Создаем сессию оплаты
            session = StripeService.create_checkout_session(
                price_id=price.id,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    'payment_id': str(payment.id),
                    'user_id': str(user.id),
                    'item_type': item_type,
                    'item_id': str(item.id)
                }
            )

            # Обновляем платеж данными из Stripe
            payment.stripe_product_id = product.id
            payment.stripe_price_id = price.id
            payment.stripe_session_id = session.id
            payment.stripe_payment_url = session.url
            payment.save()

            return Response({
                "message": "Платежная сессия создана",
                "payment_id": payment.id,
                "stripe_session_id": session.id,
                "payment_url": session.url,
                "amount": float(payment.amount)
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Если ошибка - обновляем статус платежа
            payment.payment_status = 'failed'
            payment.save()
            return Response(
                {"error": f"Ошибка создания платежной сессии: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CheckPaymentStatusAPIView(APIView):
    """
    API для проверки статуса платежа
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, payment_id):
        """
        Проверка статуса платежа
        """
        payment = get_object_or_404(Payment, id=payment_id, user=request.user)

        if payment.stripe_session_id:
            try:
                session = StripeService.retrieve_session(payment.stripe_session_id)

                # Обновляем статус платежа на основе данных из Stripe
                if session.payment_status == 'paid':
                    payment.payment_status = 'paid'
                elif session.payment_status == 'unpaid':
                    payment.payment_status = 'pending'
                payment.save()

                return Response({
                    "payment_id": payment.id,
                    "stripe_status": session.payment_status,
                    "our_status": payment.payment_status,
                    "amount_total": session.amount_total / 100 if session.amount_total else None,
                    "currency": session.currency
                })

            except Exception as e:
                return Response(
                    {"error": f"Ошибка проверки статуса: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response({
                "payment_id": payment.id,
                "our_status": payment.payment_status,
                "message": "Платеж не создан в Stripe"
            })


class PaymentSuccessAPIView(APIView):
    """
    Страница успешной оплаты
    """

    def get(self, request, payment_id):
        """
        Перенаправление после успешной оплаты
        """
        payment = get_object_or_404(Payment, id=payment_id)
        payment.payment_status = 'paid'
        payment.save()

        return Response({
            "message": "Оплата прошла успешно!",
            "payment_id": payment.id,
            "item": payment.paid_course.title if payment.paid_course else payment.paid_lesson.title,
            "amount": float(payment.amount)
        })


class PaymentCancelAPIView(APIView):
    """
    Страница отмены оплаты
    """

    def get(self, request, payment_id):
        """
        Перенаправление после отмены оплаты
        """
        payment = get_object_or_404(Payment, id=payment_id)
        payment.payment_status = 'canceled'
        payment.save()

        return Response({
            "message": "Оплата отменена",
            "payment_id": payment.id,
            "item": payment.paid_course.title if payment.paid_course else payment.paid_lesson.title
        })
