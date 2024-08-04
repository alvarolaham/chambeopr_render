from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0015_alter_proaccount_availability"),
    ]

    operations = [
        migrations.AddField(
            model_name="myuser",
            name="is_pro",
            field=models.BooleanField(default=False),
        ),
    ]
