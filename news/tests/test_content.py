import pytest
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, home_url, news_list):
    """Проверка количества новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, home_url, news_list):
    """Проверка сортировки новостей на главной странице."""
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, detail_url, comments):
    """Проверка сортировки комментариев."""
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, detail_url):
    """Анонимный пользователь не видит форму."""
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_client_has_form(client, detail_url, author):
    """Авторизованный пользователь видит форму."""
    client.force_login(author)
    response = client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


# from django.conf import settings
# from django.test import TestCase
# # Импортируем функцию reverse(), она понадобится для получения адреса страницы.
# from django.urls import reverse

# from news.models import News
# from datetime import timedelta
# from django.utils import timezone 
# from django.contrib.auth import get_user_model
# from news.forms import CommentForm
# from news.models import Comment, News

# # Получаем модель пользователя
# User = get_user_model()


# class TestHomePage(TestCase):
#     HOME_URL = reverse('news:home')

#     @classmethod
#     def setUpTestData(cls):
#         # Вычисляем текущую дату.
#         # today = datetime.today()
#         today =  timezone.now()
#         all_news = [
#             News(
#                 title=f'Новость {index}',
#                 text='Просто текст.',
#                 # Для каждой новости уменьшаем дату на index дней от today,
#                 # где index - счётчик цикла.
#                 date=today - timedelta(days=index)
#             )
#             for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
#         ]
#         News.objects.bulk_create(all_news)

#     def test_news_count(self):
#         # Загружаем главную страницу.
#         response = self.client.get(self.HOME_URL)
#         # Код ответа не проверяем, его уже проверили в тестах маршрутов.
#         # Получаем список объектов из словаря контекста.
#         object_list = response.context['object_list']
#         # Определяем количество записей в списке.
#         news_count = object_list.count()
#         # Проверяем, что на странице именно 10 новостей.
#         self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

#     def test_news_order(self):
#         response = self.client.get(self.HOME_URL)
#         object_list = response.context['object_list']
#         # Получаем даты новостей в том порядке, как они выведены на странице.
#         all_dates = [news.date for news in object_list]
#         # Сортируем полученный список по убыванию.
#         sorted_dates = sorted(all_dates, reverse=True)
#         # Проверяем, что исходный список был отсортирован правильно.
#         self.assertEqual(all_dates, sorted_dates) 

# class TestDetailPage(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(
#             title='Тестовая новость', text='Просто текст.'
#         )
#         # Сохраняем в переменную адрес страницы с новостью:
#         cls.detail_url = reverse('news:detail', args=(cls.news.id,))
#         cls.author = User.objects.create(username='Комментатор')
#         # Запоминаем текущее время:
#         now =  timezone.now()
#         # Создаём комментарии в цикле.
#         for index in range(10):
#             # Создаём объект и записываем его в переменную.
#             comment = Comment.objects.create(
#                 news=cls.news, author=cls.author, text=f'Tекст {index}',
#             )
#             # Сразу после создания меняем время создания комментария.
#             comment.created = now + timedelta(days=index)
#             # И сохраняем эти изменения.
#             comment.save()

#     def test_comments_order(self):
#         response = self.client.get(self.detail_url)
#         # Проверяем, что объект новости находится в словаре контекста
#         # под ожидаемым именем - названием модели.
#         self.assertIn('news', response.context)
#         # Получаем объект новости.
#         news = response.context['news']
#         # Получаем все комментарии к новости.
#         all_comments = news.comment_set.all()
#         # Собираем временные метки всех комментариев.
#         all_timestamps = [comment.created for comment in all_comments]
#         # Сортируем временные метки, менять порядок сортировки не надо.
#         sorted_timestamps = sorted(all_timestamps)
#         # Проверяем, что временные метки отсортированы правильно.
#         self.assertEqual(all_timestamps, sorted_timestamps) 
    
#     def test_anonymous_client_has_no_form(self):
#         response = self.client.get(self.detail_url)
#         self.assertNotIn('form', response.context)
        
#     def test_authorized_client_has_form(self):
#         # Авторизуем клиент при помощи ранее созданного пользователя.
#         self.client.force_login(self.author)
#         response = self.client.get(self.detail_url)
#         self.assertIn('form', response.context)
#         # Проверим, что объект формы соответствует нужному классу формы.
#         self.assertIsInstance(response.context['form'], CommentForm)