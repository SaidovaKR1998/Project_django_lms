from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


def home_view(request):
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LMS System - Образовательная платформа</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
            .container { background: white; border-radius: 20px; padding: 40px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); max-width: 900px; width: 90%; text-align: center; }
            .logo { font-size: 3rem; margin-bottom: 20px; color: #667eea; }
            h1 { color: #333; margin-bottom: 10px; font-size: 2.5rem; }
            .subtitle { color: #666; font-size: 1.2rem; margin-bottom: 30px; }
            .endpoints { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
            .endpoint-card { background: #f8f9fa; padding: 25px; border-radius: 15px; border-left: 4px solid #667eea; transition: transform 0.3s ease, box-shadow 0.3s ease; }
            .endpoint-card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
            .endpoint-card h3 { color: #333; margin-bottom: 10px; }
            .endpoint-card p { color: #666; margin-bottom: 15px; font-size: 0.9rem; }
            .btn { display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 25px; font-weight: 600; transition: all 0.3s ease; border: none; cursor: pointer; margin: 5px; }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
            .btn-outline { background: transparent; border: 2px solid #667eea; color: #667eea; }
            .btn-outline:hover { background: #667eea; color: white; }
            .api-info { background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; margin-right: 10px; }
            .get { background: #d4edda; color: #155724; } .post { background: #d1ecf1; color: #0c5460; }
            .put { background: #fff3cd; color: #856404; } .delete { background: #f8d7da; color: #721c24; }
            .footer { margin-top: 30px; color: #666; font-size: 0.9rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">📚</div>
            <h1>LMS Education Platform</h1>
            <p class="subtitle">Система управления обучением и курсами</p>

            <div class="endpoints">
                <div class="endpoint-card">
                    <h3>🚪 Админ панель</h3>
                    <p>Управление пользователями, курсами и уроками</p>
                    <a href="/admin/" class="btn">Перейти в админку</a>
                </div>

                <div class="endpoint-card">
                    <h3>🔐 Аутентификация</h3>
                    <p>JWT токены и регистрация</p>
                    <a href="/api/token/" class="btn btn-outline">Получить токен</a>
                </div>

                <div class="endpoint-card">
                    <h3>🎓 Курсы API</h3>
                    <p>Работа с образовательными курсами</p>
                    <a href="/api/courses/" class="btn btn-outline">API Курсы</a>
                </div>

                <div class="endpoint-card">
                    <h3>📖 Уроки API</h3>
                    <p>Управление уроками и материалами</p>
                    <a href="/api/lessons/" class="btn btn-outline">API Уроки</a>
                </div>
            </div>

            <div class="api-info">
                <h3>📡 Доступные API методы:</h3>
                <p><span class="method post">POST</span> <code>/api/users/</code> - Регистрация (доступно без токена)</p>
                <p><span class="method post">POST</span> <code>/api/token/</code> - Получить JWT токен</p>
                <p><span class="method post">POST</span> <code>/api/token/refresh/</code> - Обновить токен</p>
                <p><span class="method get">GET</span> <code>/api/courses/</code> - Список курсов (требуется токен)</p>
                <p><span class="method post">POST</span> <code>/api/courses/</code> - Создать курс (только не-модераторы)</p>
                <p><span class="method get">GET</span> <code>/api/users/profile/</code> - Мой профиль</p>
            </div>

            <div class="footer">
                <p>LMS System v2.0 | Django + DRF + JWT | 2024</p>
            </div>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


urlpatterns = [
                  path('', home_view, name='home'),
                  path('admin/', admin.site.urls),
                  path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                  path('api/', include('lms.urls')),
                  path('api/', include('users.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)