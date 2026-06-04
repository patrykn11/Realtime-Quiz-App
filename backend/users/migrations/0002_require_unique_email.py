from django.db import migrations, models


def prepare_unique_emails(apps, schema_editor):
    user_model = apps.get_model("users", "User")
    used_emails = set()

    for user in user_model.objects.order_by("pk").iterator():
        email = user.email.strip().lower()
        if not email or email in used_emails:
            email = f"legacy-{user.pk}@users.invalid"
            suffix = 1
            while email in used_emails:
                email = f"legacy-{user.pk}-{suffix}@users.invalid"
                suffix += 1

        used_emails.add(email)
        if user.email != email:
            user_model.objects.filter(pk=user.pk).update(email=email)


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(prepare_unique_emails, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
