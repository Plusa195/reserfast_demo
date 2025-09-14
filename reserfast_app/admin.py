from django.contrib import admin
from django.db import connection
from django.utils.html import format_html
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
import bcrypt
from .models import (
    TblMenu, TblMesa, TblReserva, TblReservamenu, TblReservamesa,
    TblUsuario, TblPerfil, TblGenero, TblCliente
)

def _table_exists(table_name: str) -> bool:
    try:
        return table_name in connection.introspection.table_names()
    except Exception:
        return False

class TblUsuarioCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = TblUsuario
        fields = ('s_usuario', 's_nombreusuario', 's_primerapellidousuario', 'fk_id_perfil')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        user.s_contrasenausuario = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if commit:
            user.save()
        return user

class TblUsuarioChangeForm(forms.ModelForm):
    class Meta:
        model = TblUsuario
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            password_change_url = f"/reserfast/admin_password/usuario/{self.instance.pk}/"
            self.fields['s_contrasenausuario'].help_text = mark_safe(
                f'<strong>Contraseña encriptada (no editable directamente).</strong><br>'
                f'<a href="{password_change_url}" target="_blank" style="background: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">🔑 Cambiar contraseña</a>'
            )
            self.fields['s_contrasenausuario'].widget.attrs['readonly'] = True
            self.fields['s_contrasenausuario'].widget.attrs['style'] = 'background-color: #f0f0f0; color: #666;'
            
    def save(self, commit=True):
        usuario = super().save(commit=commit)
        return usuario

class TblClienteCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput)

    class Meta:
        model = TblCliente
        fields = ('s_primernombrecliente', 's_primerapellidocliente', 's_email', 's_rut', 'fk_id_genero')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        cliente = super().save(commit=False)
        password = self.cleaned_data["password1"]
        cliente.s_contrasena = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if commit:
            cliente.save()
        return cliente

class TblClienteChangeForm(forms.ModelForm):
    class Meta:
        model = TblCliente
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            password_change_url = f"/reserfast/admin_password/cliente/{self.instance.pk}/"
            self.fields['s_contrasena'].help_text = mark_safe(
                f'<strong>Contraseña encriptada (no editable directamente).</strong><br>'
                f'<a href="{password_change_url}" target="_blank" style="background: #007cba; color: white; padding: 5px 10px; text-decoration: none; border-radius: 3px;">🔑 Cambiar contraseña</a>'
            )
            self.fields['s_contrasena'].widget.attrs['readonly'] = True
            self.fields['s_contrasena'].widget.attrs['style'] = 'background-color: #f0f0f0; color: #666;'
            
    def save(self, commit=True):
        cliente = super().save(commit=commit)
        return cliente

class TblMenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 's_titulomenu', 'i_precio', 'b_activo', 'menu_image_tag')
    search_fields = ('s_titulomenu',)
    list_filter = ('b_activo',)
    fieldsets = (
        (None, {'fields': ('s_titulomenu', 's_descripcionmenu', 's_tipomenu', 'i_precio', 's_imagen', 'b_activo')}),
    )

    readonly_fields = ('menu_image_tag',)

    def menu_image_tag(self, obj):
        try:
            if obj.s_imagen and obj.s_imagen.name and obj.s_imagen.storage.exists(obj.s_imagen.name):
                return format_html(
                    '<img src="{}" style="max-height:100px; max-width:150px; border-radius:8px;" />',
                    obj.s_imagen.url
                )
        except Exception:
            pass
        return format_html('<span style="color:#888;">{}</span>', 'Sin imagen')
    menu_image_tag.short_description = 'Vista Previa'

class TblMesaAdmin(admin.ModelAdmin):
    list_display = ('id_mesa', 's_nombremesa', 's_ubicacion', 'b_ocupado', 'b_activo')
    search_fields = ('s_nombremesa',)
    list_filter = ('b_activo', 's_ubicacion', 'b_ocupado')
    list_editable = ('b_ocupado', 'b_activo')
    actions = ['marcar_disponible', 'marcar_ocupada']

    @admin.action(description='Marcar mesas seleccionadas como Disponibles')
    def marcar_disponible(self, request, queryset):
        queryset.update(b_ocupado=0)

    @admin.action(description='Marcar mesas seleccionadas como Ocupadas')
    def marcar_ocupada(self, request, queryset):
        queryset.update(b_ocupado=1)

class TblReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fk_id_cliente', 'd_fechainicio', 'i_totalreserva', 'b_activo')
    list_filter = ('b_activo',)

class TblReservamenuAdmin(admin.ModelAdmin):
    list_display = ('id_reservamenu', 'fk_id_menu', 'fk_id_reserva', 'b_activo')

class TblReservamesaAdmin(admin.ModelAdmin):
    list_display = ('id_reservamesa', 'fk_id_reserva', 'fk_id_mesa', 'b_activo')

if _table_exists('tbl_menu'):
    admin.site.register(TblMenu, TblMenuAdmin)
if _table_exists('tbl_mesa'):
    admin.site.register(TblMesa, TblMesaAdmin)
if _table_exists('tbl_reserva'):
    admin.site.register(TblReserva, TblReservaAdmin)
if _table_exists('tbl_reservaMenu'):
    admin.site.register(TblReservamenu, TblReservamenuAdmin)
if _table_exists('tbl_reservaMesa'):
    admin.site.register(TblReservamesa, TblReservamesaAdmin)

if _table_exists('tbl_usuario'):
    @admin.register(TblUsuario)
    class TblUsuarioAdmin(admin.ModelAdmin):
        form = TblUsuarioChangeForm
        add_form = TblUsuarioCreationForm
        
        list_display = ('id_usuario', 's_usuario', 's_nombreusuario', 's_primerapellidousuario', 'get_perfil', 'b_activo', 'user_status')
        search_fields = ('s_usuario', 's_nombreusuario', 's_primerapellidousuario')
        list_filter = ('b_activo', 'fk_id_perfil')
        list_editable = ('b_activo',)
        
        fieldsets = (
            ('Información Básica', {
                'fields': ('s_usuario', 's_nombreusuario', 's_primerapellidousuario')
            }),
            ('Permisos', {
                'fields': ('fk_id_perfil', 'b_activo')
            }),
            ('Contraseña', {
                'fields': ('s_contrasenausuario',)
            }),
        )
        
        add_fieldsets = (
            ('Crear Usuario', {
                'classes': ('wide',),
                'fields': ('s_usuario', 's_nombreusuario', 's_primerapellidousuario', 'fk_id_perfil', 'password1', 'password2', 'b_activo')
            }),
        )
        
        def get_urls(self):
            from django.urls import path
            urls = super().get_urls()
            custom_urls = [
                path('<int:object_id>/password/', self.admin_site.admin_view(self.user_change_password), 
                     name='reserfast_app_tblusuario_password'),
            ]
            return custom_urls + urls
        
        def user_change_password(self, request, object_id, form_url=''):
            from django.shortcuts import redirect
            return redirect(f'/reserfast/admin_password/usuario/{object_id}/')
        
        def get_perfil(self, obj):
            if obj.fk_id_perfil:
                color = 'green' if obj.fk_id_perfil.s_nombreperfil == 'Administrador' else 'orange' if obj.fk_id_perfil.s_nombreperfil == 'Garzon' else 'blue'
                return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.fk_id_perfil.s_nombreperfil)
            return 'Sin perfil'
        get_perfil.short_description = 'Perfil'
        
        def user_status(self, obj):
            if obj.b_activo:
                return format_html('<span style="color: green;">●</span> Activo')
            return format_html('<span style="color: red;">●</span> Inactivo')
        user_status.short_description = 'Estado'
        
        def get_form(self, request, obj=None, **kwargs):
            if not obj:
                kwargs['form'] = self.add_form
            return super().get_form(request, obj, **kwargs)

if _table_exists('tbl_cliente'):
    @admin.register(TblCliente)
    class TblClienteAdmin(admin.ModelAdmin):
        form = TblClienteChangeForm
        add_form = TblClienteCreationForm
        
        list_display = ('id_cliente', 'get_nombre_completo', 's_email', 's_rut', 'get_genero', 'b_activo', 'cliente_status', 'profile_image_tag')
        search_fields = ('s_primernombrecliente', 's_primerapellidocliente', 's_email', 's_rut')
        list_filter = ('b_activo', 'fk_id_genero')
        list_editable = ('b_activo',)
        
        fieldsets = (
            ('Información Personal', {
                'fields': ('s_primernombrecliente', 's_segundonombrecliente', 's_primerapellidocliente', 's_segundoapellidocliente')
            }),
            ('Contacto', {
                'fields': ('s_email', 's_telefono', 's_rut')
            }),
            ('Información Adicional', {
                'fields': ('fk_id_genero', 'd_fecha_nacimiento', 's_foto_perfil')
            }),
            ('Estado', {
                'fields': ('b_activo',)
            }),
            ('Contraseña', {
                'fields': ('s_contrasena',)
            }),
        )
        
        add_fieldsets = (
            ('Crear Cliente', {
                'classes': ('wide',),
                'fields': ('s_primernombrecliente', 's_primerapellidocliente', 's_email', 's_rut', 'fk_id_genero', 'password1', 'password2', 'b_activo')
            }),
        )
        
        readonly_fields = ('profile_image_tag',)
        
        def get_urls(self):
            from django.urls import path
            urls = super().get_urls()
            custom_urls = [
                path('<int:object_id>/password/', self.admin_site.admin_view(self.cliente_change_password), 
                     name='reserfast_app_tblcliente_password'),
            ]
            return custom_urls + urls
        
        def cliente_change_password(self, request, object_id, form_url=''):
            from django.shortcuts import redirect
            return redirect(f'/reserfast/admin_password/cliente/{object_id}/')
        
        def get_nombre_completo(self, obj):
            nombre = f"{obj.s_primernombrecliente or ''} {obj.s_primerapellidocliente or ''}".strip()
            return nombre or 'Sin nombre'
        get_nombre_completo.short_description = 'Nombre Completo'
        
        def get_genero(self, obj):
            if obj.fk_id_genero:
                color = 'blue' if obj.fk_id_genero.s_nombregenero == 'Masculino' else 'pink'
                return format_html('<span style="color: {};">{}</span>', color, obj.fk_id_genero.s_nombregenero)
            return 'No especificado'
        get_genero.short_description = 'Género'
        
        def cliente_status(self, obj):
            if obj.b_activo:
                return format_html('<span style="color: green;">●</span> Activo')
            return format_html('<span style="color: red;">●</span> Inactivo')
        cliente_status.short_description = 'Estado'
        
        def profile_image_tag(self, obj):
            if obj.s_foto_perfil:
                try:
                    return format_html(
                        '<img src="{}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover;" />',
                        obj.s_foto_perfil.url
                    )
                except:
                    pass
            return format_html('<span style="color: #888;">Sin foto</span>')
        profile_image_tag.short_description = 'Foto'
        
        def get_form(self, request, obj=None, **kwargs):
            if not obj:
                kwargs['form'] = self.add_form
            return super().get_form(request, obj, **kwargs)

if _table_exists('tbl_perfil'):
    @admin.register(TblPerfil)
    class TblPerfilAdmin(admin.ModelAdmin):
        list_display = ('id_perfil', 's_nombreperfil', 'b_activo')
        list_filter = ('b_activo',)

if _table_exists('tbl_genero'):
    @admin.register(TblGenero)
    class TblGeneroAdmin(admin.ModelAdmin):
        list_display = ('id_genero', 's_nombregenero', 'b_activo')
        list_filter = ('b_activo',)

# Branding del admin
admin.site.site_header = 'ReserFast Admin'
admin.site.site_title = 'ReserFast Admin'
admin.site.index_title = 'Panel de Administración ReserFast'
