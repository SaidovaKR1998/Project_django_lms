from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Payment


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'is_active']
    list_filter = ['email', 'is_staff', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['email']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_date', 'get_course', 'get_lesson', 'amount', 'payment_method']
    list_filter = ['payment_method', 'payment_date', 'paid_course']
    search_fields = ['user__email', 'paid_course__title', 'paid_lesson__title']
    readonly_fields = ['payment_date']

    def get_course(self, obj):
        return obj.paid_course.title if obj.paid_course else "-"

    get_course.short_description = 'Курс'

    def get_lesson(self, obj):
        return obj.paid_lesson.title if obj.paid_lesson else "-"

    get_lesson.short_description = 'Урок'
