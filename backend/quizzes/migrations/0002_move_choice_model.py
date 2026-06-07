import django.db.models.deletion
from django.db import migrations, models


def create_tables_if_missing(apps, schema_editor):
    table_names = schema_editor.connection.introspection.table_names()
    if "quiz_question" not in table_names:
        schema_editor.create_model(apps.get_model("quizzes", "Question"))
    if "quiz_choice" not in table_names:
        schema_editor.create_model(apps.get_model("quizzes", "Choice"))


class Migration(migrations.Migration):
    dependencies = [
        ("quizzes", "0001_initial"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="Question",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("text", models.CharField(max_length=255)),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        (
                            "quiz",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="questions",
                                to="quizzes.quiz",
                            ),
                        ),
                    ],
                    options={"db_table": "quiz_question"},
                ),
                migrations.CreateModel(
                    name="Choice",
                    fields=[
                        (
                            "id",
                            models.BigAutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        ("text", models.CharField(max_length=255)),
                        ("is_correct", models.BooleanField(default=False)),
                        (
                            "question",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="choices",
                                to="quizzes.question",
                            ),
                        ),
                    ],
                    options={"db_table": "quiz_choice"},
                ),
            ],
        ),
        migrations.RunPython(
            create_tables_if_missing,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
