import csv
import os

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')
django.setup()

from .models import Category, Comment, Genre, Review, Title, TitleGenre, User


def load_users(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'email': row.get('email', ''),
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'bio': row.get('bio', ''),
                    'role': row.get('role', User.USER),
                }
            )

def load_categories(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Category.objects.get_or_create(
                slug=row['slug'],
                defaults={
                    'title': row['title'],
                    'is_published': row.get('is_published', True) == 'True'
                }
            )

def load_genres(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Genre.objects.get_or_create(
                slug=row['slug'],
                defaults={
                    'title': row['title'],
                    'is_published': row.get('is_published', True) == 'True'
                }
            )

def load_titles(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            category = None
            if row.get('category_slug'):
                try:
                    category = Category.objects.get(slug=row['category_slug'])
                except ObjectDoesNotExist:
                    print(
                        f"Категория с slug '{row['category_slug']}' не найдена"
                    )
                    continue

            Title.objects.get_or_create(
                title=row['title'],  # Используем title как уникальное поле
                defaults={
                    'description': row.get('description', ''),
                    'year': row.get('year', None),
                    'category': category,
                    'is_published': row.get('is_published', True) == 'True',
                }
            )

def load_title_genres(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                title = Title.objects.get(title=row['title'])
                genre = Genre.objects.get(slug=row['genre_slug'])
                TitleGenre.objects.get_or_create(
                    title=title,
                    genre=genre
                )
            except ObjectDoesNotExist as e:
                print(f'Ошибка при создании связи TitleGenre: {e}')

def load_reviews(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                author = User.objects.get(username=row['author_username'])
                title = Title.objects.get(title=row['title_name'])
                Review.objects.get_or_create(
                    author=author,
                    title=title,
                    defaults={
                        'text': row['text'],
                        'score': int(row['score']),
                    }
                )
            except ObjectDoesNotExist as e:
                print(f'Не удалось найти автора или произведение для отзыва: {e}')

def load_comments(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                review = Review.objects.get(id=row['review_id'])
                author = User.objects.get(username=row['author_username'])
                Comment.objects.get_or_create(
                    review=review,
                    author=author,
                    defaults={
                        'text': row['text'],
                    }
                )
            except ObjectDoesNotExist as e:
                print(f'Не удалось найти отзыв или автора для комментария: {e}')

if __name__ == '__main__':
    # Укажите пути к вашим CSV-файлам
    load_users('../static/data/users.csv')
    load_categories('../static/data/category.csv')
    load_genres('../static/data/genre.csv')
    load_titles('../static/data/titles.csv')
    load_title_genres('../static/data/genre_title.csv')
    load_reviews('../static/data/review.csv')
    load_comments('../static/data/comments.csv')
