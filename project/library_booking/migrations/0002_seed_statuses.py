from django.db import migrations


def seed_statuses(apps, schema_editor):
    Status = apps.get_model('library_booking', 'Status')
    rows = [
        ('available', 'Доступно', 'place'),
        ('unavailable', 'Недоступно', 'place'),
        ('new', 'Новая', 'booking'),
        ('approved', 'Одобрена', 'booking'),
        ('rejected', 'Отклонена', 'booking'),
    ]
    for code, label, kind in rows:
        Status.objects.get_or_create(
            code=code,
            kind=kind,
            defaults={'label': label},
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('library_booking', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_statuses, noop_reverse),
    ]
