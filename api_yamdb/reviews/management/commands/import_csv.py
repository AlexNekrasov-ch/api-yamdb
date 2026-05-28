import csv
from datetime import datetime

from django.core.management.base import BaseCommand

from reviews.models import (Category, Comment, Genre, Review, Title,
                            TitleGenre, User)


class Command(BaseCommand):
    help = 'Импорт данных из CSV-файлов в базу данных'

    def handle(self, *args, **options):
        base_path = 'static/data/'

        # Порядок импорта важен из-за внешних ключей
        import_order = [
            ('users.csv', self.import_users, 'Пользователи'),
            ('category.csv', self.import_categories, 'Категории'),
            ('genre.csv', self.import_genres, 'Жанры'),
            ('titles.csv', self.import_titles, 'Произведения'),
            ('genre_title.csv', self.import_title_genre, 'Связи жанров'),
            ('review.csv', self.import_reviews, 'Отзывы'),
            ('comments.csv', self.import_comments, 'Комментарии'),
        ]

        for filename, import_func, name in import_order:
            self.stdout.write(f'\n📥 Импорт {name} из {filename}...')
            try:
                import_func(f'{base_path}{filename}')
                self.stdout.write(
                    self.style.SUCCESS(f'  ✅ {name} успешно импортированы')
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Файл {filename} не найден!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Ошибка при импорте {filename}: {str(e)}'
                    )
                )

    def import_users(self, filepath):
        """Импорт пользователей из users.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                user, created = User.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'username': row['username'],
                        'email': row['email'],
                        'first_name': row.get('first_name', ''),
                        'last_name': row.get('last_name', ''),
                        'bio': row.get('bio', ''),
                        'role': row.get('role', 'user'),
                    }
                )
                if created:
                    count += 1
                    self.stdout.write(
                        f'    - Создан пользователь: {user.username}'
                    )
            self.stdout.write(f'    Создано {count} новых пользователей')

    def import_categories(self, filepath):
        """Импорт категорий из category.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                category, created = Category.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
                if created:
                    count += 1
                    self.stdout.write(
                        f'    - Создана категория: {category.name}'
                    )
            self.stdout.write(f'    Создано {count} новых категорий')

    def import_genres(self, filepath):
        """Импорт жанров из genre.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                genre, created = Genre.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
                if created:
                    count += 1
                    self.stdout.write(f'    - Создан жанр: {genre.name}')
            self.stdout.write(f'    Создано {count} новых жанров')

    def import_titles(self, filepath):
        """Импорт произведений из titles.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                category = None
                if row.get('category'):
                    try:
                        category = Category.objects.get(id=row['category'])
                    except Category.DoesNotExist:
                        self.stdout.write(
                            f'    ⚠️ Категория id={row["category"]} '
                            f'не найдена для "{row["name"]}"')

                title, created = Title.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'year': row['year'],
                        'category': category,
                        'description': row.get('description', ''),
                    }
                )
                if created:
                    count += 1
                    self.stdout.write(
                        f'    - Создано произведение: {title.name}'
                    )
            self.stdout.write(f'    Создано {count} новых произведений')

    def import_title_genre(self, filepath):
        """Импорт связей произведение-жанр из genre_title.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    title.genre.add(genre)
                    count += 1
                except Title.DoesNotExist:
                    self.stdout.write(
                        f'    ⚠️ Произведение id={row["title_id"]} не найдено'
                    )
                except Genre.DoesNotExist:
                    self.stdout.write(
                        f'    ⚠️ Жанр id={row["genre_id"]} не найден'
                    )
            self.stdout.write(f'    Создано {count} новых связей')

    def import_reviews(self, filepath):
        """Импорт отзывов из review.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])

                    # Преобразуем дату
                    pub_date = datetime.strptime(
                        row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ'
                    )

                    review, created = Review.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'title': title,
                            'text': row['text'],
                            'author': author,
                            'score': row['score'],
                            'pub_date': pub_date,
                        }
                    )
                    if created:
                        count += 1
                except Title.DoesNotExist:
                    self.stdout.write(
                        f'    ⚠️ Произведение id={row["title_id"]} '
                        f'не найдено для отзыва {row["id"]}')
                except User.DoesNotExist:
                    self.stdout.write(
                        f'    ⚠️ Пользователь id={row["author"]} '
                        f'не найден для отзыва {row["id"]}')
            self.stdout.write(f'    Создано {count} новых отзывов')

    def import_comments(self, filepath):
        """Импорт комментариев из comments.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])

                    # Преобразуем дату
                    pub_date = datetime.strptime(
                        row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ')

                    comment, created = Comment.objects.get_or_create(
                        id=row['id'],
                        defaults={
                            'review': review,
                            'text': row['text'],
                            'author': author,
                            'pub_date': pub_date,
                        }
                    )
                    if created:
                        count += 1
                except Review.DoesNotExist:
                    self.stdout.write(f'    ⚠️ Отзыв id={row["review_id"]} '
                                      f'не найден для комментария {row["id"]}')
                except User.DoesNotExist:
                    self.stdout.write(
                        f'    ⚠️ Пользователь id={row["author"]} '
                        f'не найден для комментария {row["id"]}')
            self.stdout.write(f'    Создано {count} новых комментариев')
