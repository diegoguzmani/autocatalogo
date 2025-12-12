from django import forms
from .models import Configuracion

class TasaForm(forms.ModelForm):
    class Meta:
        model = Configuracion
        fields = ['tasa_dolar']
        labels = {'tasa_dolar': 'Tasa del Dólar (Bs/USD)'}