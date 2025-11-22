from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Payment


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Сериализатор для публичного просмотра профилей других пользователей
    Доступна только общая информация (без пароля, фамилии, истории платежей)
    """

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name')  # Только email и имя, без фамилии


class UserPrivateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для владельца профиля (полная информация)
    """

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ('email',)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'user',
            'payment_date',
            'paid_course',
            'paid_lesson',
            'amount',
            'payment_method',
            'stripe_payment_url',  # Добавлено для Stripe
            'payment_status',  # Добавлено для Stripe
        ]
        read_only_fields = ['user', 'payment_date', 'stripe_payment_url', 'payment_status']


class UserProfileWithPaymentsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля владельца с историей платежей
    Только для владельца профиля
    """
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'payments')
        read_only_fields = ('email',)