import pytest
from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from news.models import News, Comment

User = get_user_model()


@pytest.mark.django_db
def test_pages_availability(client):
    """Проверка доступности основных страниц."""
    news = News.objects.create(title='Заголовок', text='Текст')

    urls = (
        ('news:home', None),
        ('news:detail', (news.id,)),
        ('users:login', None),
        ('users:signup', None),
    )

    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK, (
            f'Страница {name} недоступна — статус {response.status_code}'
        )


@pytest.mark.django_db
def test_availability_for_comment_edit_and_delete(client):
    """Проверка доступа к редактированию и удалению комментариев."""
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(news=news, author=author, text='Текст комментария')

    users_statuses = (
        (author, HTTPStatus.OK),
        (reader, HTTPStatus.NOT_FOUND),
    )

    for user, expected_status in users_statuses:
        client.force_login(user)
        for name in ('news:edit', 'news:delete'):
            url = reverse(name, args=(comment.id,))
            response = client.get(url)
            assert response.status_code == expected_status, (
                f'Пользователь {user.username} получил неверный статус для {name}:'
                f' {response.status_code}, ожидалось {expected_status}'
            )


@pytest.mark.django_db
def test_redirect_for_anonymous_client(client):
    """Анонимный пользователь должен получать редирект на логин-страницу."""
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Автор комментария')
    comment = Comment.objects.create(news=news, author=author, text='Текст комментария')

    login_url = reverse('users:login')

    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        expected_redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND, (
            f'Ожидался редирект (302) при доступе анонимного пользователя к {name}'
        )
        assert response.url == expected_redirect_url, (
            f'Редирект неправильный: {response.url} ≠ {expected_redirect_url}'
        )

# from http import HTTPStatus

# from django.test import TestCase
# from django.urls import reverse

# from news.models import News
# from django.contrib.auth import get_user_model

# # Импортируем класс комментария.
# from news.models import Comment, News

# # Получаем модель пользователя.
# User = get_user_model()


# class TestRoutes(TestCase):

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(title='Заголовок', text='Текст')

#     def test_pages_availability(self):
#         urls = (
#             ('news:home', None),
#             ('news:detail', (self.news.id,)),
#             ('users:login', None),
#             ('users:signup', None),
#         )
#         for name, args in urls:
#             with self.subTest(name=name):
#                 url = reverse(name, args=args)
#                 response = self.client.get(url)
#                 self.assertEqual(response.status_code, HTTPStatus.OK) 

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(title='Заголовок', text='Текст')
#         # Создаём двух пользователей с разными именами:
#         cls.author = User.objects.create(username='Лев Толстой')
#         cls.reader = User.objects.create(username='Читатель простой')
#         # От имени одного пользователя создаём комментарий к новости:
#         cls.comment = Comment.objects.create(
#             news=cls.news,
#             author=cls.author,
#             text='Текст комментария'
#         ) 
#     def test_availability_for_comment_edit_and_delete(self):
#         users_statuses = (
#             (self.author, HTTPStatus.OK),
#             (self.reader, HTTPStatus.NOT_FOUND),
#         )
#         for user, status in users_statuses:
#             # Логиним пользователя в клиенте:
#             self.client.force_login(user)
#             # Для каждой пары "пользователь - ожидаемый ответ"
#             # перебираем имена тестируемых страниц:
#             for name in ('news:edit', 'news:delete'):  
#                 with self.subTest(user=user, name=name):        
#                     url = reverse(name, args=(self.comment.id,))
#                     response = self.client.get(url)
#                     self.assertEqual(response.status_code, status) 

#     def test_redirect_for_anonymous_client(self):
#         # Сохраняем адрес страницы логина:
#         login_url = reverse('users:login')
#         # В цикле перебираем имена страниц, с которых ожидаем редирект:
#         for name in ('news:edit', 'news:delete'):
#             with self.subTest(name=name):
#                 # Получаем адрес страницы редактирования или удаления комментария:
#                 url = reverse(name, args=(self.comment.id,))
#                 # Получаем ожидаемый адрес страницы логина, 
#                 # на который будет перенаправлен пользователь.
#                 # Учитываем, что в адресе будет параметр next, в котором передаётся
#                 # адрес страницы, с которой пользователь был переадресован.
#                 redirect_url = f'{login_url}?next={url}'
#                 response = self.client.get(url)
#                 # Проверяем, что редирект приведёт именно на указанную ссылку.
#                 self.assertRedirects(response, redirect_url) 