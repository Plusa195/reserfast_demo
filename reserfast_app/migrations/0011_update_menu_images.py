from django.db import migrations


def update_menu_images(apps, schema_editor):
    Menu = apps.get_model('reserfast_app', 'TblMenu')
    # Choose a file that exists in media/menu_img to avoid 404
    existing_path = 'menu_img/menu-ejecutivo-con-pollo-compressed_kiaVAkX.jpg'
    targets = [
        'menu_img/aji_gallina.jpg',
        'menu_img/ceviche.jpg',
        'menu_img/hamburguesa.jpg',
        'menu_img/heineken.jpg',
    ]
    try:
        Menu.objects.filter(s_notas__in=targets).update(s_notas=existing_path)
    except Exception:
        # Best-effort only; ignore if table missing in non-demo DB
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('reserfast_app', '0010_sqlite_bootstrap'),
    ]

    operations = [
        migrations.RunPython(update_menu_images, migrations.RunPython.noop),
    ]
