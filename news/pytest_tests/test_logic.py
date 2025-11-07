import pytest
from http import HTTPStatus
from django.urls import reverse
from news.models import News, Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.django_db
def test_user_can_create_comment(client, django_user_model):
    """Авторизованный пользователь может создать комментарий."""
    user = django_user_model.objects.create(username='Мимо Крокодил')
    client.force_login(user)

    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', args=(news.id,))
    form_data = {'text': 'Текст комментария'}

    response = client.post(url, data=form_data)

    # Проверяем редирект на #comments после отправки формы
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'

    # Проверяем, что комментарий создан
    comment = Comment.objects.get()
    assert Comment.objects.count() == 1
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == user


@pytest.mark.django_db
def test_user_cant_use_bad_words(client, django_user_model):
    """Если текст содержит запрещённые слова — комментарий не создаётся."""
    user = django_user_model.objects.create(username='Цензор')
    client.force_login(user)

    news = News.objects.create(title='Заголовок', text='Текст')
    url = reverse('news:detail', args=(news.id,))
    bad_text = f'Какой-то текст, {BAD_WORDS[0]}, еще текст'
    form_data = {'text': bad_text}

    response = client.post(url, data=form_data)
    form = response.context['form']

    # Проверяем, что форма содержит ошибку
    errors = form.errors.get('text')
    assert errors is not None
    assert WARNING in errors

    # Проверяем, что комментарий не создан
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(client, django_user_model):
    """Автор комментария может редактировать свой комментарий."""
    author = django_user_model.objects.create(username='Автор комментария')
    client.force_login(author)
    news = News.objects.create(title='Заголовок', text='Текст')
    comment = Comment.objects.create(news=news, author=author, text='Старый текст')
    new_text = 'Обновлённый комментарий'

    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'

    response = client.post(edit_url, data={'text': new_text})

    # Проверяем, что сработал редирект
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == url_to_comments

    # Проверяем, что комментарий изменился
    comment.refresh_from_db()
    assert comment.text == new_text


@pytest.mark.django_db
def test_user_cant_edit_foreign_comment(client, django_user_model):
    """Пользователь не может редактировать чужой комментарий (получает 404)."""
    author = django_user_model.objects.create(username='Автор')
    reader = django_user_model.objects.create(username='Читатель')
    news = News.objects.create(title='Заголовок', text='Текст')
    comment = Comment.objects.create(news=news, author=author, text='Коммент')

    client.force_login(reader)
    edit_url = reverse('news:edit', args=(comment.id,))

    response = client.post(edit_url, data={'text': 'Попытка изменить'})

    # Проверяем, что 404
    assert response.status_code == HTTPStatus.NOT_FOUND

    # Комментарий не изменился
    comment.refresh_from_db()
    assert comment.text == 'Коммент'

# from http import HTTPStatus

# from django.contrib.auth import get_user_model
# from django.test import Client, TestCase
# from django.urls import reverse

# # Импортируем из файла с формами список стоп-слов и предупреждение формы.
# # Загляните в news/forms.py, разберитесь с их назначением.
# from news.forms import BAD_WORDS, WARNING
# from news.models import Comment, News

# User = get_user_model()


# class TestCommentCreation(TestCase):
#     # Текст комментария понадобится в нескольких местах кода, 
#     # поэтому запишем его в атрибуты класса.
#     COMMENT_TEXT = 'Текст комментария'

#     @classmethod
#     def setUpTestData(cls):
#         cls.news = News.objects.create(title='Заголовок', text='Текст')
#         # Адрес страницы с новостью.
#         cls.url = reverse('news:detail', args=(cls.news.id,))
#         # Создаём пользователя и клиент, логинимся в клиенте.
#         cls.user = User.objects.create(username='Мимо Крокодил')
#         cls.auth_client = Client()
#         cls.auth_client.force_login(cls.user)
#         # Данные для POST-запроса при создании комментария.
#         cls.form_data = {'text': cls.COMMENT_TEXT}

#     def test_user_can_create_comment(self):
#         # Совершаем запрос через авторизованный клиент.
#         response = self.auth_client.post(self.url, data=self.form_data)
#         # Проверяем, что редирект привёл к разделу с комментами.
#         self.assertRedirects(response, f'{self.url}#comments')
#         # Считаем количество комментариев.
#         comments_count = Comment.objects.count()
#         # Убеждаемся, что есть один комментарий.
#         self.assertEqual(comments_count, 1)
#         # Получаем объект комментария из базы.
#         comment = Comment.objects.get()
#         # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
#         self.assertEqual(comment.text, self.COMMENT_TEXT)
#         self.assertEqual(comment.news, self.news)
#         self.assertEqual(comment.author, self.user)

#     def test_user_cant_use_bad_words(self):
#         # Формируем данные для отправки формы; текст включает
#         # первое слово из списка стоп-слов.
#         bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
#         # Отправляем запрос через авторизованный клиент.
#         response = self.auth_client.post(self.url, data=bad_words_data)
#         form = response.context['form']
#         # Проверяем, есть ли в ответе ошибка формы.
#         self.assertFormError(
#             form=form,
#             field='text',
#             errors=WARNING
#         )
#         # Дополнительно убедимся, что комментарий не был создан.
#         comments_count = Comment.objects.count()
#         self.assertEqual(comments_count, 0)

# class TestCommentEditDelete(TestCase):
#     # Тексты для комментариев не нужно дополнительно создавать 
#     # (в отличие от объектов в БД), им не нужны ссылки на self или cls, 
#     # поэтому их можно перечислить просто в атрибутах класса.
#     COMMENT_TEXT = 'Текст комментария'
#     NEW_COMMENT_TEXT = 'Обновлённый комментарий'

#     @classmethod
#     def setUpTestData(cls):
#         # Создаём новость в БД.
#         cls.news = News.objects.create(title='Заголовок', text='Текст')
#         # Формируем адрес блока с комментариями, который понадобится для тестов.
#         news_url = reverse('news:detail', args=(cls.news.id,))  # Адрес новости.
#         cls.url_to_comments = news_url + '#comments'  # Адрес блока с комментариями.
#         # Создаём пользователя - автора комментария.
#         cls.author = User.objects.create(username='Автор комментария')
#         # Создаём клиент для пользователя-автора.
#         cls.author_client = Client()
#         # "Логиним" пользователя в клиенте.
#         cls.author_client.force_login(cls.author)
#         # Делаем всё то же самое для пользователя-читателя.
#         cls.reader = User.objects.create(username='Читатель')
#         cls.reader_client = Client()
#         cls.reader_client.force_login(cls.reader)
#         # Создаём объект комментария.
#         cls.comment = Comment.objects.create(
#             news=cls.news,
#             author=cls.author,
#             text=cls.COMMENT_TEXT
#         )
#         # URL для редактирования комментария.
#         cls.edit_url = reverse('news:edit', args=(cls.comment.id,)) 
#         # URL для удаления комментария.
#         cls.delete_url = reverse('news:delete', args=(cls.comment.id,))  
#         # Формируем данные для POST-запроса по обновлению комментария.
#         cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

#     def test_author_can_edit_comment(self):
#         # Выполняем запрос на редактирование от имени автора комментария.
#         response = self.author_client.post(self.edit_url, data=self.form_data)
#         # Проверяем, что сработал редирект.
#         self.assertRedirects(response, self.url_to_comments)
#         # Обновляем объект комментария.
#         self.comment.refresh_from_db()
#         # Проверяем, что текст комментария соответствует обновленному.
#         self.assertEqual(self.comment.text, self.NEW_COMMENT_TEXT)

#     def test_user_cant_edit_comment_of_another_user(self):
#         # Выполняем запрос на редактирование от имени другого пользователя.
#         response = self.reader_client.post(self.edit_url, data=self.form_data)
#         # Проверяем, что вернулась 404 ошибка.
#         self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
#         # Обновляем объект комментария.
#         self.comment.refresh_from_db()
#         # Проверяем, что текст остался тем же, что и был.
#         self.assertEqual(self.comment.text, self.COMMENT_TEXT)