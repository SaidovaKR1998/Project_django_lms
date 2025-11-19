from django.core.exceptions import ValidationError
from urllib.parse import urlparse
import re


def validate_youtube_url(value):
    """
    Валидатор для проверки, что ссылка ведет только на YouTube
    """
    if value is None or value == '':
        return

    # Парсим URL
    parsed_url = urlparse(value)

    # Проверяем домен
    allowed_domains = ['youtube.com', 'www.youtube.com', 'youtu.be', 'www.youtu.be']

    if parsed_url.netloc not in allowed_domains:
        raise ValidationError(
            f'Ссылка должна вести на YouTube. Получен домен: {parsed_url.netloc}'
        )

    # Дополнительная проверка с помощью регулярного выражения
    youtube_pattern = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.+$'
    if not re.match(youtube_pattern, value):
        raise ValidationError('Некорректная ссылка на YouTube')


class YouTubeURLValidator:
    """
    Класс-валидатор для проверки YouTube ссылок
    """

    def __call__(self, value):
        validate_youtube_url(value)

    def __init__(self, field):
        self.field = field
