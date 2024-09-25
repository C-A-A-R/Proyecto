from django import forms
from import_export.forms import ExportForm
from django.utils.translation import gettext_lazy as _

class CustomExportForm(ExportForm):
    start_date = forms.DateField(
        label=_("Fecha Inicial"), 
        required=False, 
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label=_("Fecha Final"), 
        required=False, 
        widget=forms.widgets.DateInput(attrs={'type': 'date'})
    )

class DataUserExportForm(CustomExportForm):
    # Selección de campos para exportar
    FIELD_CHOICES = [
        ('username', 'Nombre de Usuario'),
        ('first_name', 'Nombre'),
        ('last_name', 'Apellido'),
        ('last_login', 'Último Inicio de Sesión'),
        ('email', 'Correo'),
        ('date_joined', 'Fecha de Registro'),
        ('phone', 'Número de Teléfono'),
        ('sector', 'Sector de Vivienda'),
        ('is_active', 'Estado de Usuario')
    ]
    fields_to_export = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_("Campos para exportar"),
        required=False
    )

class PaymentExportForm(CustomExportForm):
    # Selección de campos para exportar
    FIELD_CHOICES = [
        ('auth_user', 'ID de Usuario'),
        ('first_name', 'Nombre'),
        ('last_name', 'Apellido'),
        ('publicity_name', 'Nombre de Publicidad'),
        # ('publicity', 'Publicidad'),
        ('days_transmit', 'Días de Transmisión'),
        ('sending_day', 'Fecha de Pago'),
        ('reference_number', 'Referencia de Pago'),
        # ('payment_proof', 'Captura de Pago'),
        ('payment_status', 'Estado de Pago')
    ]
    fields_to_export = forms.MultipleChoiceField(
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label=_("Campos para exportar"),
        required=False
    )
