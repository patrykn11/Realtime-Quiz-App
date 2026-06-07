from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("quizzes", "0003_remove_legacy_content_types"),
    ]

    operations = [
        migrations.AddField(
            model_name="quiz",
            name="owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="quizzes",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
