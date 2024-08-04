# myapp/migrations/0019_add_pro_account_created_at.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0018_merge_0016_auto_20240721_1536_0017_add_is_pro_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="myuser",
            name="pro_account_created_at",
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
