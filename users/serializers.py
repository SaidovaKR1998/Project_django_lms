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
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name')


# СЕРИАЛИЗАТОР ДЛЯ PAYMENT
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
            'payment_method'
        ]
        read_only_fields = ['user', 'payment_date']


# СЕРИАЛИЗАТОР ДЛЯ ПРОФИЛЯ С ПЛАТЕЖАМИ
class UserProfileWithPaymentsSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'payments')
        read_only_fields = ('email',)