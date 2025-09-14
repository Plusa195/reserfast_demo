from django.db import models

class TblGenero(models.Model):
    id_genero = models.AutoField(primary_key=True)
    s_nombregenero = models.CharField(db_column='s_nombreGenero', max_length=50, blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_genero'
        verbose_name = "Genero"
    def __str__(self):
        return self.s_nombregenero

class TblPerfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    s_nombreperfil = models.CharField(db_column='s_nombrePerfil', max_length=50, blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_perfil'
        verbose_name = "Perfil"
    def __str__(self):
        return f'{self.id_perfil} {self.s_nombreperfil}'

class TblUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    fk_id_perfil = models.ForeignKey(TblPerfil, models.DO_NOTHING, db_column='fk_id_perfil', blank=True, null=True)
    s_nombreusuario = models.CharField(db_column='s_nombreUsuario', blank=True, null=True, max_length=80)
    s_primerapellidousuario = models.CharField(db_column='s_primerApellidoUsuario', max_length=80, blank=True, null=True)
    s_segundoapellidousuario = models.CharField(db_column='s_segundoApellidoUsuario', max_length=80, blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    s_usuario = models.CharField(db_column='s_usuario', max_length=80, blank=False, null=False)
    s_contrasenausuario = models.CharField(db_column='s_contrasenaUsuario', max_length=80, blank=False, null=False)
    fk_id_genero = models.ForeignKey(TblGenero, models.DO_NOTHING, db_column='fk_id_genero', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'tbl_usuario'
        verbose_name = "Usuario"
    def __str__(self):
        return f'{self.s_nombreusuario} {self.s_primerapellidousuario}'

class TblCliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    s_primernombrecliente = models.CharField(db_column='s_primerNombreCliente', max_length=80, blank=True, null=True)
    s_segundonombrecliente = models.CharField(db_column='s_segundoNombreCliente', max_length=80, blank=True, null=True)
    s_primerapellidocliente = models.CharField(db_column='s_primerApellidoCliente', max_length=80, blank=True, null=True)
    s_segundoapellidocliente = models.CharField(db_column='s_segundoApellidoCliente', max_length=80, blank=True, null=True)
    s_rut = models.CharField(max_length=13, blank=True, null=True)
    s_email = models.CharField(max_length=50, blank=True, null=True)
    s_contrasena = models.CharField(max_length=80, blank=True, null=True)
    fk_id_genero = models.ForeignKey(TblGenero, models.PROTECT, db_column='fk_id_genero', blank=True, null=True)
    s_foto_perfil = models.ImageField(upload_to='perfil_img/', blank=True, null=True, verbose_name="Foto de Perfil")
    s_telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono")
    d_fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name="Fecha de Nacimiento")
    b_activo = models.BooleanField(default=True, blank=False, null=False, db_column='b_activo')
    class Meta:
        managed = False
        db_table = 'tbl_cliente'
        ordering = ['s_primernombrecliente']
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

class TblIngrediente(models.Model):
    id_ingrediente = models.AutoField(primary_key=True)
    s_nombreingrediente = models.CharField(db_column='s_nombreIngrediente', max_length=100, blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_ingrediente'
        verbose_name = "Ingrediente"

class TblMenu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    fk_id_usuario = models.ForeignKey(TblUsuario, models.DO_NOTHING, db_column='fk_id_usuario', blank=True, null=True)
    s_titulomenu = models.CharField(db_column='s_tituloMenu', max_length=50, blank=True, null=True)
    s_descripcionmenu = models.CharField(db_column='s_descripcionMenu', max_length=1000, blank=True, null=True)
    s_tipomenu = models.CharField(db_column='s_tipoMenu', max_length=80, blank=False, null=False)
    i_precio = models.IntegerField(blank=True, null=True)
    s_imagen = models.ImageField(upload_to='menu_img/', blank=True, null=True, help_text='Imagen del menú')
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_menu'
        verbose_name = "Menu"
    def __str__(self):
        return self.s_titulomenu if self.s_titulomenu else f"Menu {self.id_menu}"

class TblMenuingrediente(models.Model):
    id_menuingrediente = models.AutoField(db_column='id_menuIngrediente', primary_key=True)
    fk_id_menu = models.ForeignKey(TblMenu, models.DO_NOTHING, db_column='fk_id_menu', blank=True, null=True)
    fk_id_ingrediente = models.ForeignKey(TblIngrediente, models.DO_NOTHING, db_column='fk_id_ingrediente', blank=True, null=True)
    b_activo = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'tbl_menuIngrediente'
        verbose_name = "MenuIngrediente"

class TblMesa(models.Model):
    id_mesa = models.AutoField(primary_key=True)
    fk_id_usuario = models.ForeignKey(TblUsuario, models.DO_NOTHING, db_column='fk_id_usuario', blank=True, null=True)
    s_nombremesa = models.CharField(db_column='s_nombreMesa', max_length=100, blank=True, null=True)
    s_descripcionmesa = models.CharField(db_column='s_descripcionMesa', max_length=100, blank=True, null=True)
    d_fechacreacion = models.DateField(db_column='d_fechaCreacion', blank=True, null=True)
    s_ubicacion = models.CharField(max_length=30, blank=True, null=True)
    b_ocupado = models.IntegerField()
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_mesa'
        verbose_name = "Mesa"
    def __str__(self):
        return f'{self.id_mesa} {self.s_nombremesa} {self.s_descripcionmesa}'

class TblReserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fk_id_cliente = models.ForeignKey(TblCliente, models.DO_NOTHING, db_column='fk_id_cliente', blank=True, null=True)
    d_fechainicio = models.DateField(db_column='d_fechaInicio', blank=True, null=True)
    i_totalreserva = models.IntegerField(db_column='i_totalReserva', blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    fk_id_usuario = models.ForeignKey(TblUsuario, models.DO_NOTHING, db_column='fk_id_usuario', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'tbl_reserva'
        verbose_name = "Reserva"

class TblReservamenu(models.Model):
    id_reservamenu = models.AutoField(db_column='id_reservaMenu', primary_key=True)
    fk_id_menu = models.ForeignKey(TblMenu, models.DO_NOTHING, db_column='fk_id_menu', blank=True, null=True)
    fk_id_reserva = models.ForeignKey(TblReserva, models.DO_NOTHING, db_column='fk_id_reserva', blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_reservaMenu'
        verbose_name = "ReservaMenu"

class TblReservamesa(models.Model):
    id_reservamesa = models.AutoField(db_column='id_reservaMesa', primary_key=True)
    fk_id_reserva = models.ForeignKey(TblReserva, models.DO_NOTHING, db_column='fk_id_reserva', blank=True, null=True)
    fk_id_mesa = models.ForeignKey(TblMesa, models.DO_NOTHING, db_column='fk_id_mesa', blank=True, null=True)
    b_activo = models.BooleanField(default=True)
    class Meta:
        managed = False
        db_table = 'tbl_reservaMesa'
        verbose_name = "ReservaMesa"