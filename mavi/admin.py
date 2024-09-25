from import_export.admin import ExportActionModelAdmin
from import_export.formats.base_formats import XLSX, Format
from django.contrib import admin
from django import forms
from .models import DataUser, Publicity, Payment
from .utils import make_naive
from import_export import resources, fields
from .form_admin import DataUserExportForm, PaymentExportForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.utils.html import format_html
from reportlab.lib.pagesizes import A4,landscape
from reportlab.pdfgen import canvas
from io import BytesIO


class PDF(Format):
    def get_title(self):
        return "pdf"

    def get_extension(self):
        return "pdf"

    def get_content_type(self):
        return "application/pdf"

    def export_data(self, dataset, **kwargs):
        buffer = BytesIO()
        pdf_canvas = canvas.Canvas(buffer, pagesize=landscape(A4))  # Usamos la orientación horizontal
        width, height = landscape(A4)

        # Definir las coordenadas iniciales
        x = 50
        y = height - 50  # Reducimos el margen superior

        # Título del documento
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(x, y, "Exportación de Datos de Usuario")
        y -= 40

        # Escribir los nombres de las columnas
        pdf_canvas.setFont("Helvetica-Bold", 12)
        column_width = (width - 100) // len(dataset.headers)  # Ajustar el ancho de las columnas

        for i, col in enumerate(dataset.headers):
            pdf_canvas.drawString(x + (i * column_width), y, col)

        y -= 20

        # Escribir los datos
        pdf_canvas.setFont("Helvetica", 10)
        for row in dataset.dict:
            if y < 50:  # Si la posición Y es demasiado baja, saltar a una nueva página
                pdf_canvas.showPage()
                pdf_canvas.setFont("Helvetica-Bold", 12)
                y = height - 50  # Reiniciar la posición Y para la nueva página
                
                # Dibujar los encabezados en la nueva página
                for i, col in enumerate(dataset.headers):
                    pdf_canvas.drawString(x + (i * column_width), y, col)
                y -= 20
                pdf_canvas.setFont("Helvetica", 10)

            for i, col in enumerate(dataset.headers):
                pdf_canvas.drawString(x + (i * column_width), y, str(row[col]))
            y -= 20

        # Terminar el PDF
        pdf_canvas.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def is_binary(self):
        return True


admin.site.unregister(Group)


@admin.register(Publicity)
class PublicityAdmin(admin.ModelAdmin):
    list_display = ['first_name',
                    'last_name',
                    'contract_date',
                    'publicity_name',
                    'publicity_image',
                    'review_result']
    list_editable = ['review_result']
    
    def publicity_image(self, obj):
        if obj.publicity:
            return format_html(
                '<a href="#popup_{}"><img src="{}" class="image-thumbnail" /></a>'
                '<div id="popup_{}" class="image-popup">'
                '<a href="#">&times;</a>'
                '<img src="{}" />'
                '</div>',
                obj.pk,
                obj.publicity.url.replace('/admin_app', '' ),
                obj.pk,
                obj.publicity.url.replace('/admin_app', '' )
            )
        return "No Existe Publicidad"
    publicity_image.short_description = 'Publicidad'
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }

    def first_name(self, obj):
            return obj.auth_user.first_name if obj.auth_user else 'N/A'
    first_name.short_description = 'Nombre'
    
    def last_name(self, obj):
            return obj.auth_user.last_name if obj.auth_user else 'N/A'
    last_name.short_description = 'Apellido'
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('auth_user')
        queryset = queryset.filter(review_result='pending')
        return queryset


class PaymentResource(resources.ModelResource):
    # Definir campos personalizados para exportación
    auth_user = fields.Field(attribute='publicity_id__auth_user__id', column_name='ID de Usuario')
    first_name = fields.Field(attribute='publicity_id__auth_user__first_name', column_name='Nombre')
    last_name = fields.Field(attribute='publicity_id__auth_user__last_name', column_name='Apellido')
    publicity_name = fields.Field(attribute='publicity_id__publicity_name', column_name='Nombre de Publicidad')
    # publicity = fields.Field(attribute='publicity_id__publicity', column_name='Publicidad')  # Cambiado a publicity
    days_transmit = fields.Field(attribute='publicity_id__days_transmit', column_name='Días de Transmisión')
    sending_day = fields.Field(attribute='sending_day', column_name='Fecha de Pago')
    reference_number = fields.Field(attribute='reference_number', column_name='Referencia de Pago')
    # payment_proof = fields.Field(attribute='payment_proof', column_name='Captura de Pago')  # Cambiado a payment_proof
    payment_status = fields.Field(attribute='payment_status', column_name='Estado de Pago')

    class Meta:
        model = Payment
        fields = (
            'auth_user',
            'first_name',
            'last_name',
            'publicity_name',
            # 'publicity',  # Cambiado a publicity
            'days_transmit',
            'sending_day',
            'reference_number',
            # 'payment_proof',  # Cambiado a payment_proof
            'payment_status'
        )
        export_order = fields  # Opcional: Define el orden de exportación
    
    def get_export_headers(self, fields=None):
        """
        Genera los encabezados de las columnas en base a los campos seleccionados.
        """
        headers = []
        # Si hay campos seleccionados, obtenemos sus nombres
        for field in fields or self.get_fields():
            headers.append(self.fields[field].column_name or field)
        return headers

    
    def export_resource(self, obj, fields=None):
        """
        Exporta un objeto en función de los campos seleccionados.

        :param obj: El objeto (instancia de Payment) a exportar.
        :param fields: Los campos que se deben exportar.
        :returns: Una lista con los valores exportados.
        """
        data = []
        
        # Mapeo de campos de Payment y campos relacionados de publicity y auth_user
        field_mapping = {
            'auth_user': obj.publicity_id.auth_user.id if obj.publicity_id and obj.publicity_id.auth_user else 'N/A',
            'first_name': obj.publicity_id.auth_user.first_name if obj.publicity_id and obj.publicity_id.auth_user else 'N/A',
            'last_name': obj.publicity_id.auth_user.last_name if obj.publicity_id and obj.publicity_id.auth_user else 'N/A',
            'publicity_name': obj.publicity_id.publicity_name if obj.publicity_id else 'N/A',
            # 'publicity': obj.publicity_id.publicity if obj.publicity_id else 'N/A',
            'days_transmit': obj.publicity_id.days_transmit if obj.publicity_id else 'N/A',
            'sending_day': make_naive(obj.sending_day),  # Convertir la fecha a naive
            'reference_number': obj.reference_number,
            # 'payment_proof_base64': obj.payment_proof,  # Si necesitas convertir la imagen, puedes hacerlo aquí
            'payment_status': obj.payment_status
        }

        # Si se especifican campos, exportar solo esos
        if fields:
            for field in fields:
                data.append(field_mapping.get(field, 'N/A'))
        else:
            # Si no hay campos especificados, exportar todos los campos por defecto
            for field in self.Meta.fields:
                data.append(field_mapping.get(field, 'N/A'))

        return data
    

@admin.register(Payment)
class PaymentAdmin(ExportActionModelAdmin):
    resource_class = PaymentResource
    list_display = [
        'first_name',
        'publicity_name',
        'publicity_image',
        'days_transmit',
        'sending_day',
        'reference_number',
        'payment_proof_image',
        'payment_status'
    ]
    list_editable = ['payment_status']

    # Agregar el filtro personalizado
    list_filter = ['payment_status']
    
    # Activar el formulario para seleccionar el formato de exportación
    export_form_class = PaymentExportForm  # Usamos el formulario personalizado
    export_template_name = 'admin/import_export/export.html'  # Plantilla por defecto
    
# Métodos para mostrar imágenes en el admin
    def publicity_image(self, obj):
        if obj.publicity_id and obj.publicity_id.publicity:
            return format_html(
                '<a href="#popup_{}"><img src="{}" class="image-thumbnail" /></a>'
                '<div id="popup_{}" class="image-popup">'
                '<a href="#">&times;</a>'
                '<img src="{}" />'
                '</div>',
                obj.pk,
                obj.publicity_id.publicity.url.replace('/admin_app', ''),
                obj.pk,
                obj.publicity_id.publicity.url.replace('/admin_app', '')
            )
        return "No Hay Publicidad"
    publicity_image.short_description = 'Publicidad'

    def payment_proof_image(self, obj):
        if obj.payment_proof:
            return format_html(
                '<a href="#popup__{}"><img src="{}" class="image-thumbnail" /></a>'
                '<div id="popup__{}" class="image-popup">'
                '<a href="#">&times;</a>'
                '<img src="{}" />'
                '</div>',
                obj.pk,
                obj.payment_proof.url.replace('/admin_app', ''),
                obj.pk,
                obj.payment_proof.url.replace('/admin_app', '')
            )
        return "No Hay Captura de Pago"
    payment_proof_image.short_description = 'Captura de Pago'

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
        
    def auth_user(self, obj):
        return obj.publicity_id.auth_user.id if obj.publicity_id else 'N/A'
    auth_user.short_description = 'ID de Usuario'
    
    def first_name(self, obj):
        return obj.publicity_id.auth_user.first_name if obj.publicity_id else 'N/A'
    first_name.short_description = 'Nombre'
    
    def last_name(self, obj):
        return obj.publicity_id.auth_user.last_name if obj.publicity_id else 'N/A'
    last_name.short_description = 'Apellido'
    
    def publicity_name(self, obj):
        return obj.publicity_id.publicity_name if obj.publicity_id else 'N/A'
    publicity_name.short_description = 'Nombre de Publicidad'

    def days_transmit(self, obj):
        return obj.publicity_id.days_transmit if obj.publicity_id else 'N/A'
    days_transmit.short_description = 'dias de transmición'
    
    def get_export_data(self, file_format, request, queryset, *args, **kwargs):
        """
        Personalizar los datos exportados para incluir solo los campos seleccionados.
        Si el formato es PDF, elimina las columnas relacionadas con imágenes.
        """
        export_form = kwargs.get('export_form') or self.export_form_class(
            formats=self.get_export_formats(),
            resources=[self.resource_class()],
            data=request.POST
        )

        if export_form.is_valid():
            # Obtenemos los campos seleccionados
            fields_to_export = export_form.cleaned_data.get('fields_to_export', [])

            # Verificamos si hay campos seleccionados
            if fields_to_export:
                # Exportar solo los campos seleccionados
                dataset = self.resource_class().export(queryset, export_fields=fields_to_export)
            else:
                # Si no se seleccionan columnas, exportamos todos los campos, excepto imágenes en PDF
                fields_to_export = [field for field in self.resource_class().Meta.fields]

                dataset = self.resource_class().export(queryset, export_fields=fields_to_export)

            # Exportar los datos en el formato solicitado
            return file_format.export_data(dataset)
        else:
            # Manejar el caso de un formulario inválido
            print("Errores del formulario: ", export_form.errors)
            return None
    
    def get_queryset(self, request):
        # Obtener el queryset base
        queryset = super().get_queryset(request).select_related('publicity_id__auth_user')

        if request.method == 'POST':
            form = self.export_form_class(
                formats=self.get_export_formats(),  
                resources=[self.resource_class()],
                data=request.POST
            )

            if form.is_valid():
                # Fechas
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')

                if start_date:
                    queryset = queryset.filter(publicity_id__auth_user__date_joined__gte=start_date)
                if end_date:
                    queryset = queryset.filter(publicity_id__auth_user__date_joined__lte=end_date)

        return queryset

    def get_export_formats(self):
        """Retorna los formatos disponibles para la exportación"""
        return [
            XLSX,
            PDF  # Añadimos el formato PDF
        ]




class DataUserResource(resources.ModelResource):
    # Definir campos personalizados para exportación
    username = fields.Field(attribute='auth_user__username', column_name='Nombre de Usuario')
    first_name = fields.Field(attribute='auth_user__first_name', column_name='Nombre')
    last_name = fields.Field(attribute='auth_user__last_name', column_name='Apellido')
    last_login = fields.Field(attribute='auth_user__last_login', column_name='Ultimo Inicio de Sesión')
    email = fields.Field(attribute='auth_user__email', column_name='Correo')
    date_joined = fields.Field(attribute='auth_user__date_joined', column_name='Fecha de Registro')
    is_active = fields.Field(attribute='auth_user__is_active', column_name='Estado de Usuario')
    phone = fields.Field(attribute='phone', column_name='Numero de Telefono')
    sector = fields.Field(attribute='sector', column_name='Sector de vivienda')

    class Meta:
        model = DataUser
        fields = (
            'username', 
            'first_name', 
            'last_name', 
            'last_login', 
            'email', 
            'date_joined',
            'phone', 
            'sector', 
            'is_active'
        )

    def get_export_headers(self, fields=None):
        """
        Genera los encabezados de las columnas en base a los campos seleccionados.
        """
        headers = []
        # Si hay campos seleccionados, obtenemos sus nombres
        for field in fields or self.get_fields():
            headers.append(self.fields[field].column_name or field)
        return headers

    def export_resource(self, obj, fields=None):
        """
        Exporta un objeto en función de los campos seleccionados.

        :param obj: El objeto (instancia de DataUser) a exportar.
        :param fields: Los campos que se deben exportar.
        :returns: Una lista con los valores exportados.
        """
        data = []
        
        # Mapeo de campos de DataUser y campos relacionados de auth_user
        field_mapping = {
            'username': obj.auth_user.username if obj.auth_user else 'N/A',
            'first_name': obj.auth_user.first_name if obj.auth_user else 'N/A',
            'last_name': obj.auth_user.last_name if obj.auth_user else 'N/A',
            'last_login': make_naive(obj.auth_user.last_login) if obj.auth_user else 'N/A',
            'email': obj.auth_user.email if obj.auth_user else 'N/A',
            'date_joined': make_naive(obj.auth_user.date_joined) if obj.auth_user else 'N/A',
            'phone': obj.phone,
            'sector': obj.sector,
            'is_active': obj.auth_user.is_active if obj.auth_user else 'N/A',
        }

        # Si se especifican campos, exportar solo esos
        if fields:
            for field in fields:
                data.append(field_mapping.get(field, 'N/A'))
        else:
            # Si no hay campos especificados, exportar todos los campos por defecto
            for field in self.Meta.fields:
                data.append(field_mapping.get(field, 'N/A'))

        return data
    
    



class FormatSelectForm(forms.Form):
    FORMAT_CHOICES = [
        ('xlsx', 'Excel (XLSX)'),
        ('pdf', 'PDF')
    ]
    export_format = forms.ChoiceField(choices=FORMAT_CHOICES, label='Formato de exportación')


@admin.register(DataUser)
class DataUserAdmin(ExportActionModelAdmin):
    resource_class = DataUserResource
    list_display = [
        'username',
        'first_name',
        'last_name',
        'last_login',
        'email',
        'phone',
        'sector',
        'date_joined',
        'is_active'
    ]
    
    # Activar el formulario para seleccionar el formato de exportación
    export_form_class = DataUserExportForm  # Usamos el formulario personalizado
    export_template_name = 'admin/import_export/export.html'  # Plantilla por defecto
    
        # Métodos para obtener datos del modelo relacionado auth_user
    def username(self, obj):
        return obj.auth_user.username if obj.auth_user else 'N/A'
    username.short_description = 'Nombre de Usuario'
    
    def first_name(self, obj):
        return obj.auth_user.first_name if obj.auth_user else 'N/A'
    first_name.short_description = 'Nombre'

    def last_name(self, obj):
        return obj.auth_user.last_name if obj.auth_user else 'N/A'
    last_name.short_description = 'Apellido'

    def last_login(self, obj):
        return obj.auth_user.last_login if obj.auth_user else 'N/A'
    last_login.short_description = 'Ultimo Inicio de Sesión'

    def email(self, obj):
        return obj.auth_user.email if obj.auth_user else 'N/A'
    email.short_description = 'Correo'
    
    def date_joined(self, obj):
        return obj.auth_user.date_joined if obj.auth_user else 'N/A'
    date_joined.short_description = 'Fecha de Registro'
    
    def is_active(self, obj):
        return obj.auth_user.is_active if obj.auth_user else 'N/A'
    is_active.short_description = 'Estado de Usuario'
    
    
    def get_queryset(self, request):
        # Obtener el queryset base
        queryset = super().get_queryset(request).select_related('auth_user')

        if request.method == 'POST':
            form = self.export_form_class(
                formats=self.get_export_formats(),  
                resources=[self.resource_class()],
                data=request.POST
            )

            if form.is_valid():
                # Fechas
                start_date = form.cleaned_data.get('start_date')
                end_date = form.cleaned_data.get('end_date')

                if start_date:
                    queryset = queryset.filter(auth_user__date_joined__gte=start_date)
                if end_date:
                    queryset = queryset.filter(auth_user__date_joined__lte=end_date)

        return queryset


    def get_export_data(self, file_format, request, queryset, *args, **kwargs):
        """
        Personalizar los datos exportados para incluir solo los campos seleccionados.
        """
        export_form = kwargs.get('export_form') or self.export_form_class(
            formats=self.get_export_formats(),
            resources=[self.resource_class()],
            data=request.POST
        )

        if export_form.is_valid():
            # Obtenemos los campos seleccionados
            fields_to_export = export_form.cleaned_data.get('fields_to_export', [])

            # Verificamos si hay campos seleccionados
            if fields_to_export:
                # Exportar solo los campos seleccionados
                dataset = self.resource_class().export(queryset, export_fields=fields_to_export)
            else:
                
                fields_to_export = [field for field in self.resource_class().Meta.fields]
                
                # Exportar los datos con los campos seleccionados (o todos si no se seleccionaron campos)
                dataset = self.resource_class().export(queryset, export_fields=fields_to_export)
                
            # Exportar los datos en el formato solicitado
            return file_format.export_data(dataset)
        else:
            # Manejar el caso de un formulario inválido
            print("Errores del formulario: ", export_form.errors)
            return None

    
    
    def get_export_formats(self):
        """Retorna los formatos disponibles para la exportación"""
        return [
            XLSX,
            PDF  # Añadimos el formato PDF
        ]

    
    
