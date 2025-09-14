from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms
import bcrypt
from .models import TblUsuario, TblCliente

class PasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        help_text="La contraseña debe tener al menos 8 caracteres."
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden")
            if len(password1) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres")

        return cleaned_data

@staff_member_required
def change_usuario_password(request, user_id):
    usuario = get_object_or_404(TblUsuario, id_usuario=user_id)
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            usuario.s_contrasenausuario = hashed_password.decode('utf-8')
            usuario.save()
            
            messages.success(request, f'✅ Contraseña cambiada exitosamente para {usuario.s_usuario}')
            return HttpResponseRedirect('/admin/reserfast_app/tblusuario/')
    else:
        form = PasswordChangeForm()

    context = {
        'form': form,
        'usuario': usuario,
        'title': f'Cambiar contraseña de {usuario.s_usuario}',
        'opts': TblUsuario._meta,
        'original': usuario,
    }
    return render(request, 'admin/change_password.html', context)

@staff_member_required
def change_cliente_password(request, cliente_id):
    cliente = get_object_or_404(TblCliente, id_cliente=cliente_id)
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cliente.s_contrasena = hashed_password.decode('utf-8')
            cliente.save()
            
            nombre = f"{cliente.s_primernombrecliente} {cliente.s_primerapellidocliente}".strip()
            messages.success(request, f'✅ Contraseña cambiada exitosamente para {nombre}')
            return HttpResponseRedirect('/admin/reserfast_app/tblcliente/')
    else:
        form = PasswordChangeForm()

    nombre = f"{cliente.s_primernombrecliente} {cliente.s_primerapellidocliente}".strip()
    context = {
        'form': form,
        'cliente': cliente,
        'title': f'Cambiar contraseña de {nombre}',
        'opts': TblCliente._meta,
        'original': cliente,
    }
    return render(request, 'admin/change_password.html', context)
