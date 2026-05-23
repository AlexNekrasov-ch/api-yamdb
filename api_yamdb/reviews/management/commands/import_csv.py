import csv
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from reviews.models import Category, Genre, Title, TitleGenre, Review, Comment
from django.utils import timezone
from datetime import datetime

User = get_user_model()


class Command(BaseCommand):
    help = 'Import data from CSV files into the database'

    def handle(self, *args, **options):
        # Путь к папке с CSV файлами
        base_path = 'static/data/'
        
        # Порядок импорта важен из-за внешних ключей
        import_order = [
            ('users.csv', self.import_users),
            ('category.csv', self.import_categories),
            ('genre.csv', self.import_genres),
            ('titles.csv', self.import_titles),
            ('genre_title.csv', self.import_title_genre),
            ('review.csv', self.import_reviews),
            ('comments.csv', self.import_comments),
        ]
        
        for filename, import_func in import_order:
            self.stdout.write(f'Importing {filename}...')
            try:
                import_func(f'{base_path}{filename}')
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully imported {filename}')
                )
            except FileNotFoundError:
                self.stdout.write(
                    self.style.ERROR(f'File {filename} not found!')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error importing {filename}: {str(e)}')
                )
    
    def import_users(self, filepath):
        """Импорт пользователей из users.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
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
                    self.stdout.write(f'  Created user: {user.username}')
    
    def import_categories(self, filepath):
        """Импорт категорий из category.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                category, created = Category.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
                if created:
                    self.stdout.write(f'  Created category: {category.name}')
    
    def import_genres(self, filepath):
        """Импорт жанров из genre.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                genre, created = Genre.objects.get_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'slug': row['slug'],
                    }
                )
                if created:
                    self.stdout.write(f'  Created genre: {genre.name}')
    
    def import_titles(self, filepath):
        """Импорт произведений из titles.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Получаем объект категории
                category = None
                if row.get('category'):
                    try:
                        category = Category.objects.get(id=row['category'])
                    except Category.DoesNotExist:
                        self.stdout.write(
                            f'  Warning: Category id={row["category"]} not found for title {row["name"]}'
                        )
                
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
                    self.stdout.write(f'  Created title: {title.name}')
    
    def import_title_genre(self, filepath):
        """Импорт связей произведение-жанр из genre_title.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    genre = Genre.objects.get(id=row['genre_id'])
                    
                    title_genre, created = TitleGenre.objects.get_or_create(
                        title=title,
                        genre=genre
                    )
                    if created:
                        self.stdout.write(
                            f'  Linked title "{title.name}" with genre "{genre.name}"'
                        )
                except Title.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: Title id={row["title_id"]} not found'
                    )
                except Genre.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: Genre id={row["genre_id"]} not found'
                    )
    
    def import_reviews(self, filepath):
        """Импорт отзывов из review.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    title = Title.objects.get(id=row['title_id'])
                    author = User.objects.get(id=row['author'])
                    
                    # Преобразуем дату из строки
                    pub_date = datetime.strptime(row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    
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
                        self.stdout.write(
                            f'  Created review by {author.username} for "{title.name}"'
                        )
                except Title.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: Title id={row["title_id"]} not found for review {row["id"]}'
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: User id={row["author"]} not found for review {row["id"]}'
                    )
    
    def import_comments(self, filepath):
        """Импорт комментариев из comments.csv"""
        with open(filepath, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    review = Review.objects.get(id=row['review_id'])
                    author = User.objects.get(id=row['author'])
                    
                    # Преобразуем дату из строки
                    pub_date = datetime.strptime(row['pub_date'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    
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
                        self.stdout.write(
                            f'  Created comment by {author.username} on review {review.id}'
                        )
                except Review.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: Review id={row["review_id"]} not found for comment {row["id"]}'
                    )
                except User.DoesNotExist:
                    self.stdout.write(
                        f'  Warning: User id={row["author"]} not found for comment {row["id"]}'
                    )
