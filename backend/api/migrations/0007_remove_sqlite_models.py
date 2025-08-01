from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_transcript_unique_together'),
    ]

    operations = [
        # No operations needed as we're using MongoDB
        # Django's auth tables will remain in SQLite
    ] 