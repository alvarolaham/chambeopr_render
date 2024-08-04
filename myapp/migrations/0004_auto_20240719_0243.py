from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_myuser_is_pro_myuser_pro_account_created_at"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name="myuser",
                    name="is_pro",
                    field=models.BooleanField(default=False),
                ),
                migrations.AddField(
                    model_name="myuser",
                    name="pro_account_created_at",
                    field=models.DateTimeField(blank=True, null=True),
                ),
            ],
            database_operations=[],
        ),
    ]
