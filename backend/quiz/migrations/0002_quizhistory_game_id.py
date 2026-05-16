import uuid
from django.db import migrations, models


def populate_game_ids(apps, schema_editor):
    QuizHistory = apps.get_model("quiz", "QuizHistory")
    for history in QuizHistory.objects.filter(game_id__isnull=True):
        history.game_id = uuid.uuid4()
        history.save(update_fields=["game_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("quiz", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="quizhistory",
            name="game_id",
            field=models.UUIDField(db_index=True, null=True),
        ),
        migrations.RunPython(populate_game_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="quizhistory",
            name="game_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4),
        ),
    ]
