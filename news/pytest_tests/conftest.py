import pytest
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def author(db):
    """Создает пользователя-автора."""
    return User.objects.create(username='Комментатор')


@pytest.fixture
def news(db):
    """Создает одну новость."""
    return News.objects.create(
        title='Тестовая новость',
        text='Просто текст.'
    )


@pytest.fixture
def news_list(db):
    """Создает список новостей для главной страницы."""
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(news, author):
    """Создает 10 комментариев с разными датами."""
    now = timezone.now()
    comments_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comments_list.append(comment)
    return comments_list


@pytest.fixture
def detail_url(news):
    """Возвращает URL страницы деталей новости."""
    return reverse('news:detail', args=(news.id,))


@pytest.fixture
def home_url():
    """Возвращает URL главной страницы."""
    return reverse('news:home')


