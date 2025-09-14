from django import forms
from django.utils import timezone
from .models import TblCliente, TblUsuario, TblMesa, TblMenu, TblReserva, TblGenero
import bcrypt

class ClienteLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese su email',
            'id': 'typeEmailX'
        }),
        label="Email",
        required=True
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese Contraseña'
        }),
        label="Contraseña",
        required=True
    )

class ClienteForm(forms.ModelForm):
    s_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese Contraseña'
        }),
        label="Contraseña",
        required=True
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme Contraseña'
        }),
        label="Confirmar Contraseña",
        required=True
    )

    class Meta:
        model = TblCliente
        fields = [
            's_primernombrecliente', 
            's_segundonombrecliente', 
            's_primerapellidocliente',
            's_segundoapellidocliente',
            's_rut',
            's_email',
            'fk_id_genero'
        ]
        widgets = {
            's_primernombrecliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            's_segundonombrecliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre (opcional)'
            }),
            's_primerapellidocliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer apellido'
            }),
            's_segundoapellidocliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo apellido (opcional)'
            }),
            's_rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9'
            }),
            's_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'fk_id_genero': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_s_rut(self):
        rut = self.cleaned_data.get('s_rut')
        if TblCliente.objects.filter(s_rut=rut).exists():
            raise forms.ValidationError("Este RUT ya está registrado.")
        return rut

    def clean_s_email(self):
        email = self.cleaned_data.get('s_email')
        if TblCliente.objects.filter(s_email=email).exists():
            raise forms.ValidationError("Este email ya está registrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('s_contrasena')
        confirmar = cleaned_data.get('confirmar_contrasena')
        
        if contrasena and confirmar and contrasena != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        if contrasena and len(contrasena) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        
        return cleaned_data

    def save(self, commit=True):
        cliente = super().save(commit=False)
        contrasena = self.cleaned_data['s_contrasena']
        cliente.s_contrasena = bcrypt.hashpw(
            contrasena.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        if commit:
            cliente.save()
        return cliente

class UsuarioLoginForm(forms.Form):
    usuario = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese usuario',
            'id': 'typeEmailX'
        }),
        label="Usuario",
        required=True
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingrese Contraseña'
        }),
        label="Contraseña",
        required=True
    )

class UsuarioForm(forms.ModelForm):
    s_contrasenausuario = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese Contraseña'
        }),
        label="Contraseña",
        required=True
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme Contraseña'
        }),
        label="Confirmar Contraseña",
        required=True
    )

    class Meta:
        model = TblUsuario
        fields = [
            's_nombreusuario',
            's_primerapellidousuario',
            's_segundoapellidousuario',
            's_usuario',
            'fk_id_genero',
            'fk_id_perfil'
        ]
        widgets = {
            's_nombreusuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre'
            }),
            's_primerapellidousuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer apellido'
            }),
            's_segundoapellidousuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo apellido (opcional)'
            }),
            's_usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario'
            }),
            'fk_id_genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fk_id_perfil': forms.Select(attrs={
                'class': 'form-control'
            })
        }

    def clean_s_usuario(self):
        usuario = self.cleaned_data.get('s_usuario')
        if TblUsuario.objects.filter(s_usuario=usuario).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return usuario

    def clean(self):
        cleaned_data = super().clean()
        contrasena = cleaned_data.get('s_contrasenausuario')
        confirmar = cleaned_data.get('confirmar_contrasena')
        
        if contrasena and confirmar and contrasena != confirmar:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        if contrasena and len(contrasena) < 6:
            raise forms.ValidationError("La contraseña debe tener al menos 6 caracteres.")
        
        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        contrasena = self.cleaned_data['s_contrasenausuario']
        usuario.s_contrasenausuario = bcrypt.hashpw(
            contrasena.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        if commit:
            usuario.save()
        return usuario

class CrearReservaForm(forms.Form):
    fecha_reserva = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().strftime('%Y-%m-%d')
        }),
        label="Fecha de reserva",
        required=True
    )
    mesa = forms.ModelChoiceField(
        queryset=TblMesa.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Mesa",
        empty_label="-- Seleccione una mesa --"
    )
    menus = forms.ModelMultipleChoiceField(
        queryset=TblMenu.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label="Menús",
        required=True
    )

    def __init__(self, *args, **kwargs):
        mesas = kwargs.pop('mesas', None)
        menus = kwargs.pop('menus', None)
        super(CrearReservaForm, self).__init__(*args, **kwargs)
        
        if mesas is not None:
            self.fields['mesa'].queryset = mesas
        if menus is not None:
            self.fields['menus'].queryset = menus

    def clean_fecha_reserva(self):
        fecha = self.cleaned_data.get('fecha_reserva')
        if fecha and fecha < timezone.now().date():
            raise forms.ValidationError("La fecha debe ser hoy o una fecha futura.")
        return fecha

class EditarMesaForm(forms.ModelForm):
    class Meta:
        model = TblMesa
        fields = ['s_nombremesa', 's_descripcionmesa', 's_ubicacion', 'b_ocupado']
        widgets = {
            's_nombremesa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la mesa'
            }),
            's_descripcionmesa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción'
            }),
            's_ubicacion': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('Interior', 'Interior'),
                ('Terraza', 'Terraza'),
                ('Patio', 'Patio'),
                ('VIP', 'VIP'),
            ]),
            'b_ocupado': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                (0, 'Disponible'),
                (1, 'Ocupada'),
            ]),
        }

    def clean_s_nombremesa(self):
        nombre = self.cleaned_data.get('s_nombremesa')
        if not nombre:
            raise forms.ValidationError("El nombre de la mesa es obligatorio.")
        return nombre

class EditarReservaForm(CrearReservaForm):
    """Formulario para editar una reserva existente, reutilizando la lógica de CrearReservaForm."""
    def __init__(self, *args, **kwargs):
        self.reserva = kwargs.pop('reserva', None)
        super().__init__(*args, **kwargs)
        self.fields['menus'].widget.attrs.update({'class': 'form-check-input'})

    def clean(self):
        cleaned = super().clean()
        return cleaned

class EditarPerfilForm(forms.ModelForm):
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña actual (para confirmar cambios)'
        }),
        label="Contraseña actual",
        required=False
    )
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña (opcional)'
        }),
        label="Nueva contraseña",
        required=False
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        }),
        label="Confirmar nueva contraseña",
        required=False
    )

    class Meta:
        model = TblCliente
        fields = [
            's_primernombrecliente', 
            's_segundonombrecliente', 
            's_primerapellidocliente',
            's_segundoapellidocliente',
            's_rut',
            's_email',
            'fk_id_genero',
            's_foto_perfil',
            's_telefono',
            'd_fecha_nacimiento'
        ]
        widgets = {
            's_primernombrecliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer nombre'
            }),
            's_segundonombrecliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo nombre (opcional)'
            }),
            's_primerapellidocliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primer apellido'
            }),
            's_segundoapellidocliente': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Segundo apellido (opcional)'
            }),
            's_rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9'
            }),
            's_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'ejemplo@correo.com'
            }),
            'fk_id_genero': forms.Select(attrs={
                'class': 'form-control'
            }),
            's_foto_perfil': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            's_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'd_fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EditarPerfilForm, self).__init__(*args, **kwargs)

    def clean_s_rut(self):
        rut = self.cleaned_data.get('s_rut')
        if rut and self.user:
            existing = TblCliente.objects.filter(s_rut=rut).exclude(id_cliente=self.user.id_cliente)
            if existing.exists():
                raise forms.ValidationError("Este RUT ya está registrado por otro usuario.")
        return rut

    def clean_s_email(self):
        email = self.cleaned_data.get('s_email')
        if email and self.user:
            existing = TblCliente.objects.filter(s_email=email).exclude(id_cliente=self.user.id_cliente)
            if existing.exists():
                raise forms.ValidationError("Este email ya está registrado por otro usuario.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        contrasena_actual = cleaned_data.get('contrasena_actual')
        nueva_contrasena = cleaned_data.get('nueva_contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')
        
        if nueva_contrasena or confirmar_contrasena:
            if not contrasena_actual:
                raise forms.ValidationError("Debe ingresar su contraseña actual para cambiarla.")
            
            if nueva_contrasena != confirmar_contrasena:
                raise forms.ValidationError("Las nuevas contraseñas no coinciden.")
            
            if len(nueva_contrasena) < 6:
                raise forms.ValidationError("La nueva contraseña debe tener al menos 6 caracteres.")
            
            if self.user:
                if not bcrypt.checkpw(contrasena_actual.encode('utf-8'), self.user.s_contrasena.encode('utf-8')):
                    raise forms.ValidationError("La contraseña actual es incorrecta.")
        
        return cleaned_data

    def save(self, commit=True):
        cliente = super().save(commit=False)
        nueva_contrasena = self.cleaned_data.get('nueva_contrasena')
        
        if nueva_contrasena:
            cliente.s_contrasena = bcrypt.hashpw(
                nueva_contrasena.encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
        
        if commit:
            cliente.save()
        return cliente

class EditarPerfilEmpleadoForm(forms.ModelForm):
    contrasena_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña actual'}),
        label="Contraseña actual",
        required=False
    )
    nueva_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}),
        label="Nueva contraseña",
        required=False
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'}),
        label="Confirmar nueva contraseña",
        required=False
    )

    class Meta:
        model = TblUsuario
        fields = [
            's_nombreusuario',
            's_primerapellidousuario',
            's_segundoapellidousuario',
            's_usuario',
            'fk_id_genero',
        ]
        widgets = {
            's_nombreusuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'}),
            's_primerapellidousuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Primer apellido'}),
            's_segundoapellidousuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Segundo apellido (opcional)'}),
            's_usuario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'}),
            'fk_id_genero': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.usuario_obj = kwargs.pop('usuario_obj', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        nueva = cleaned.get('nueva_contrasena')
        confirmar = cleaned.get('confirmar_contrasena')
        actual = cleaned.get('contrasena_actual')
        if nueva or confirmar:
            if not actual:
                raise forms.ValidationError('Debe ingresar su contraseña actual para cambiarla.')
            if nueva != confirmar:
                raise forms.ValidationError('Las nuevas contraseñas no coinciden.')
            if nueva and len(nueva) < 6:
                raise forms.ValidationError('La nueva contraseña debe tener al menos 6 caracteres.')
            if self.usuario_obj and not bcrypt.checkpw(actual.encode('utf-8'), self.usuario_obj.s_contrasenausuario.encode('utf-8')):
                raise forms.ValidationError('La contraseña actual es incorrecta.')
        return cleaned

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nueva = self.cleaned_data.get('nueva_contrasena')
        if nueva:
            usuario.s_contrasenausuario = bcrypt.hashpw(nueva.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if commit:
            usuario.save()
        return usuario
