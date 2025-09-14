from django.db import migrations, connection


def bootstrap_sqlite(apps, schema_editor):
    # Only for SQLite demo environments
    if connection.vendor != 'sqlite':
        return

    ddl = []

    # Genero
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_genero (
            id_genero INTEGER PRIMARY KEY AUTOINCREMENT,
            s_nombreGenero VARCHAR(50),
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # Perfil
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_perfil (
            id_perfil INTEGER PRIMARY KEY AUTOINCREMENT,
            s_nombrePerfil VARCHAR(50),
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # Usuario
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_usuario (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_perfil INTEGER,
            s_nombreUsuario VARCHAR(80),
            s_primerApellidoUsuario VARCHAR(80),
            s_segundoApellidoUsuario VARCHAR(80),
            b_activo INTEGER DEFAULT 1,
            s_usuario VARCHAR(80) NOT NULL,
            s_contrasenaUsuario VARCHAR(80) NOT NULL,
            fk_id_genero INTEGER
        );
        """
    )

    # Cliente
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_cliente (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            s_primerNombreCliente VARCHAR(80),
            s_segundoNombreCliente VARCHAR(80),
            s_primerApellidoCliente VARCHAR(80),
            s_segundoApellidoCliente VARCHAR(80),
            s_rut VARCHAR(13),
            s_email VARCHAR(50),
            s_contrasena VARCHAR(80),
            fk_id_genero INTEGER,
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # Ingrediente
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_ingrediente (
            id_ingrediente INTEGER PRIMARY KEY AUTOINCREMENT,
            s_nombreIngrediente VARCHAR(100),
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # Menu
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_menu (
            id_menu INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_usuario INTEGER,
            s_tituloMenu VARCHAR(50),
            s_descripcionMenu VARCHAR(1000),
            s_tipoMenu VARCHAR(80) NOT NULL,
            i_precio INTEGER,
            s_notas TEXT,
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # MenuIngrediente
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_menuIngrediente (
            id_menuIngrediente INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_menu INTEGER,
            fk_id_ingrediente INTEGER,
            b_activo INTEGER
        );
        """
    )

    # Mesa
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_mesa (
            id_mesa INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_usuario INTEGER,
            s_nombreMesa VARCHAR(100),
            s_descripcionMesa VARCHAR(100),
            d_fechaCreacion DATE,
            s_ubicacion VARCHAR(30),
            b_ocupado INTEGER DEFAULT 0,
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # Reserva
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_reserva (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_cliente INTEGER,
            d_fechaInicio DATE,
            i_totalReserva INTEGER,
            b_activo INTEGER DEFAULT 1,
            fk_id_usuario INTEGER
        );
        """
    )

    # ReservaMenu
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_reservaMenu (
            id_reservaMenu INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_menu INTEGER,
            fk_id_reserva INTEGER,
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    # ReservaMesa
    ddl.append(
        """
        CREATE TABLE IF NOT EXISTS tbl_reservaMesa (
            id_reservaMesa INTEGER PRIMARY KEY AUTOINCREMENT,
            fk_id_reserva INTEGER,
            fk_id_mesa INTEGER,
            b_activo INTEGER DEFAULT 1
        );
        """
    )

    with connection.cursor() as cursor:
        for stmt in ddl:
            cursor.execute(stmt)

        # Seed data if empty
        cursor.execute("SELECT COUNT(*) FROM tbl_perfil")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tbl_perfil (id_perfil, s_nombrePerfil, b_activo) VALUES (?, ?, 1)",
                [
                    (1, 'Administrador'),
                    (2, 'Garzon'),
                    (4, 'Cocina'),
                ],
            )

        cursor.execute("SELECT COUNT(*) FROM tbl_genero")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tbl_genero (s_nombreGenero, b_activo) VALUES (?, 1)",
                [
                    ('Masculino',),
                    ('Femenino',),
                    ('Otro',),
                ],
            )

        cursor.execute("SELECT COUNT(*) FROM tbl_mesa")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tbl_mesa (s_nombreMesa, s_descripcionMesa, s_ubicacion, b_ocupado, b_activo) VALUES (?, ?, ?, 0, 1)",
                [
                    ('Mesa 1', 'Cerca de la ventana', 'Interior'),
                    ('Mesa 2', 'Esquina', 'Interior'),
                    ('Mesa 3', 'Terraza techada', 'Terraza'),
                    ('Mesa 4', 'VIP', 'VIP'),
                ],
            )

        cursor.execute("SELECT COUNT(*) FROM tbl_menu")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO tbl_menu (s_tituloMenu, s_descripcionMenu, s_tipoMenu, i_precio, s_notas, b_activo) VALUES (?, ?, ?, ?, ?, 1)",
                [
                    ('Ceviche', 'Pescado fresco con limón y cebolla', 'Entrada', 6500, 'menu_img/ceviche.jpg'),
                    ('Hamburguesa Italiana', 'Pan, palta y tomate', 'Comida Rapida', 8200, 'menu_img/hamburguesa.jpg'),
                    ('Aji de gallina', 'Clásico peruano', 'Almuerzo', 7900, 'menu_img/aji_gallina.jpg'),
                    ('Heineken', 'Cerveza helada', 'Bebida', 2500, 'menu_img/heineken.jpg'),
                ],
            )


class Migration(migrations.Migration):

    dependencies = [
        ('reserfast_app', '0009_delete_authgroup_delete_authgrouppermissions_and_more'),
    ]

    operations = [
        migrations.RunPython(bootstrap_sqlite, migrations.RunPython.noop),
    ]
