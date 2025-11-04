from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Простая view для главной страницы
def home_view(request):
    html = """
    <html>
        <body>
            <h1>Добро пожаловать в LMS систему!</h1>
            <p>Доступные эндпоинты:</p>
            <ul>
                <li><a href="/admin/">Админка</a></li>
                <li><a href="/api/courses/">API Курсы</a></li>
                <li><a href="/api/lessons/">API Уроки</a></li>
                <li><a href="/api/users/">API Пользователи</a></li>
            </ul>
        </body>
    </html>
    """
    return HttpResponse(html)

urlpatterns = [
    path('', home_view, name='home'),  # Добавляем главную страницу
    path('admin/', admin.site.urls),
    path('api/', include('lms.urls')),
#    path('api/', include('users.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
