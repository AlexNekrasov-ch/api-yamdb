from django.db.models import Avg


def get_title_rating(title):
    """
    Средняя оценка произведения по отзывам (целое число) или None.
    Подключение в TitleSerializer (разработчик 2):
        rating = serializers.SerializerMethodField()
        def get_rating(self, obj):
            return get_title_rating(obj)
    """
    rating = title.reviews.aggregate(avg_score=Avg('score'))['avg_score']
    if rating is None:
        return None
    return int(rating)
