from django import forms
from .models import usuarios


class LoginForm(forms.Form):
    correo = forms.EmailField(
        label="", 
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'correo', 
                'class': 'form-input'     
            }
        )
    )
    
    contrasena = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                'placeholder': '**********',
                'class': 'form-input'     
            }
        )
    )

class UsuarioForm(forms.Form):
    nombre = forms.CharField(
        label='Nombre',
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre completo'
        })
    )
    correo = forms.EmailField(
        label='Correo',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        })
    )
    contrasena = forms.CharField(
        label='Contraseña',
        max_length=200,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña (opcional en modificación)'
        })
    )
    rol = forms.BooleanField(
        label='Es Administrador',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    ruc = forms.CharField(
        label='RUT',
        max_length=12,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'RUT'
        })
    )

#Formulario exxtra para csv
class UploadCSVForm(forms.Form):
    archivo = forms.FileField(label="Seleccionar archivo CSV")