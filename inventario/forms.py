from django import forms
from .models import Configuracion

class TasaForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['tasa_dolar', 'tasa_euro']
        labels = {
            'tasa_dolar': 'Tasa Dólar BCV ($)',
            'tasa_euro': 'Tasa Euro BCV (€)'
        }
        widgets = {
            'tasa_dolar': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg border-success fw-bold', 
                'step': '0.01',
                'placeholder': 'Ej: 50.12'
            }),
            'tasa_euro': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg border-primary fw-bold', 
                'step': '0.01',
                'placeholder': 'Ej: 54.30'
            })
        }