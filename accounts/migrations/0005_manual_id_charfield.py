from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20250930_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='id',
            field=models.CharField(max_length=36, primary_key=True, serialize=False, unique=True),
        ),
    ]

