from django.db import migrations


def remove_legacy_content_types(apps, schema_editor):
    content_type = apps.get_model("contenttypes", "ContentType")
    content_type.objects.filter(app_label__in=("choices", "questions")).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("quizzes", "0002_move_choice_model"),
    ]

    operations = [
        migrations.RunPython(
            remove_legacy_content_types,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
