import csv
import os

import django
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_yamdb.settings')
django.setup()

from .models import Category, Comment, Genre, Review, Title, TitleGenre, User

DATA_DIR = settings.BASE_DIR / 'static' / 'data'


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
                    'name': row['name']
                }
            )

def load_genres(csv_file_path):
    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            Genre.objects.get_or_create(
                slug=row['slug'],
                defaults={
                    'name': row['name']
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

            # Преобразуем year в число, если поле существует и не пустое
            year_value = None
            if row.get('year'):
                try:
                    year_value = int(row['year'])
                except ValueError:
                    print(
                        f"Некорректный год: {row['year']} "
                        f"для фильма {row.get('title', 'Unknown')}"
                    )
                    continue

            Title.objects.get_or_create(
                name=row['name'],
                defaults={
                    'description': row.get('description', ''),
                    'year': year_value,
                    'category': category
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
    load_users('DATA_DIR/users.csv')
    load_categories('DATA_DIR/category.csv')
    load_genres('DATA_DIR/genre.csv')
    load_titles('DATA_DIR/titles.csv')
    load_title_genres('DATA_DIR/genre_title.csv')
    load_reviews('DATA_DIR/review.csv')
    load_comments('DATA_DIR/comments.csv')
