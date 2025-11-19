from rest_framework.pagination import PageNumberPagination

class LessonCoursePagination(PageNumberPagination):
    """
    Пагинатор для уроков и курсов
    """
    page_size = 10  # Количество элементов на странице по умолчанию
    page_size_query_param = 'page_size'  # Параметр для изменения количества элементов на странице
    max_page_size = 50  # Максимальное количество элементов на странице
