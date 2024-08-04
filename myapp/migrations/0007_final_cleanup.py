from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "myapp",
            "0006_remove_myuser_bio_remove_myuser_profile_picture_and_more",
        ),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Your SQL commands here
                "DROP TABLE IF EXISTS pro_account CASCADE;",
                "DROP TABLE IF EXISTS service CASCADE;",
                "DROP TABLE IF EXISTS user_profile CASCADE;",
                "DROP TABLE IF EXISTS user_service CASCADE;",
                # Remove any leftover sequences
                "DROP SEQUENCE IF EXISTS pro_account_id_seq CASCADE;",
                "DROP SEQUENCE IF EXISTS service_id_seq CASCADE;",
                "DROP SEQUENCE IF EXISTS user_profile_id_seq CASCADE;",
                "DROP SEQUENCE IF EXISTS user_service_id_seq CASCADE;",
            ],
            reverse_sql=["SELECT 1;"],  # Do nothing in reverse
        ),
    ]
