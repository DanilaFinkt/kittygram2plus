from rest_framework import viewsets
from rest_framework.throttling import ScopedRateThrottle
# from rest_framework.throttling import AnonRateThrottle
# from rest_framework.pagination import LimitOffsetPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Achievement, Cat, User

from .serializers import AchievementSerializer, CatSerializer, UserSerializer
from .permissions import OwnerOrReadOnly, ReadOnly
from .throttling import WorkingHoursRateThrottle
from .pagination import CatsPagination


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Устанавливаем разрешение
    permission_classes = (OwnerOrReadOnly,)
    # Если кастомный тротлинг-класс вернёт True - запросы будут обработаны
    # Если он вернёт False - все запросы будут отклонены
    throttle_classes = (WorkingHoursRateThrottle, ScopedRateThrottle)

    # Для любых пользователей установим кастомный лимит 1 запрос в минуту
    throttle_scope = 'low_request'
    # throttle_classes = (AnonRateThrottle,)  # Подключили класс AnonRateThrottle

    # Даже если на уровне проекта установлен PageNumberPagination
    # Для котиков будет работать LimitOffsetPagination
    # pagination_class = LimitOffsetPagination
    # GET http://127.0.0.1:8000/cats/?limit=2&offset=4
    # Такой GET-запрос вернёт два объекта, с пятого по шестой
    # (или меньше, если в результате запроса менее 6 объектов

    # Вот он наш собственный класс пагинации с page_size=20
    # pagination_class = CatsPagination

    # Указываем фильтрующий бэкенд DjangoFilterBackend
    # Из библиотеки django-filter
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    # Временно отключим пагинацию на уровне вьюсета,
    # так будет удобнее настраивать фильтрацию
    pagination_class = None
    # Фильтровать будем по полям color и birth_year модели Cat
    filterset_fields = ('color', 'birth_year')
    search_fields = ('name',)
    ordering_fields = ('name', 'birth_year')
    ordering = ('birth_year',)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # Если в GET-запросе требуется получить информацию об объекте
        if self.action == 'retrieve':
            # Вернём обновлённый перечень используемых пермишенов
            return (ReadOnly(),)
        # Для остальных ситуаций оставим текущий перечень пермишенов без изменений
        return super().get_permissions()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
