from django import forms
from .models import TblMenu

class MenuForm(forms.ModelForm):
    class Meta:
        model = TblMenu
        fields = ['s_titulomenu', 's_descripcionmenu', 's_tipomenu', 'i_precio']
        exclude = ('b_activo',)
        widgets = {
            's_titulomenu': forms.TextInput(attrs={'class': 'form-control'}),
            's_descripcionmenu': forms.TextInput(attrs={'class': 'form-control'}),
            's_tipomenu': forms.TextInput(attrs={'class': 'form-control'}),
            'i_precio': forms.TextInput(attrs={'class': 'form-control'}),
        }
        