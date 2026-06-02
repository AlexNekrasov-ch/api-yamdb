from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_alter_title_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='title',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name='titles',
                to='reviews.category',
                verbose_name='Категория',
            ),
        ),
    ]
