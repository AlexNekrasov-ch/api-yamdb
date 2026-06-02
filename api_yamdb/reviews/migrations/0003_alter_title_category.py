from django.db import migrations, models


def assign_null_categories(apps, schema_editor):
    Title = apps.get_model('reviews', 'Title')
    Category = apps.get_model('reviews', 'Category')
    first_category = Category.objects.first()
    if first_category is None:
        first_category = Category.objects.create(
            name='Uncategorized', slug='uncategorized'
        )
    Title.objects.filter(category__isnull=True).update(
        category=first_category
    )


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_alter_title_description'),
    ]

    operations = [
        migrations.RunPython(
            assign_null_categories,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='title',
            name='category',
            field=models.ForeignKey(
                blank=True,
                on_delete=models.deletion.PROTECT,
                related_name='titles',
                to='reviews.category',
                verbose_name='Категория',
            ),
        ),
    ]
