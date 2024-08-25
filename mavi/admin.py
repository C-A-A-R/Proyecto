from import_export import resources, fields
from import_export.admin import ExportActionModelAdmin
from import_export.formats.base_formats import XLSX  # Puedes cambiar a otro formato si lo prefieres

from openpyxl import Workbook
from openpyxl.drawing.image import Image as ExcelImage
import io
from PIL import Image as PilImage

from django.http import HttpResponse
from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.models import Group
from .models import Publicity, DataUser, Payment
from django.utils import timezone

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

# Función para redimensionar imágenes
def resize_image(image, max_width, max_height):
    # Redimensionar la imagen manteniendo la relación de aspecto
    width_ratio = max_width / image.width
    height_ratio = max_height / image.height
    new_ratio = min(width_ratio, height_ratio)
    
    new_width = int(image.width * new_ratio)
    new_height = int(image.height * new_ratio)
    
    return image.resize((new_width, new_height), PilImage.Resampling.LANCZOS)

# Función para exportar datos con imágenes y ajustar tamaño de celdas
def export_with_images(queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos de Pagos"

    headers = [
        'ID de Usuario', 'Nombre', 'Apellido', 'Nombre de Publicidad', 
        'Publicidad', 'Dias De Trasnmision', 'Fecha de Pago', 
        'Referencia De Pago', 'Captura de Pago', 'Estado de Pago'
    ]
    ws.append(headers)

    # Definir tamaños para redimensionar las imágenes
    max_img_width = 300  # Ancho máximo en píxeles
    max_img_height = 200  # Altura máxima en píxeles

    for row_num, obj in enumerate(queryset, start=2):  # Comienza desde la segunda fila porque la primera es el encabezado
        row_data = [
            obj.publicity_id.auth_user.id if obj.publicity_id else 'N/A',
            obj.publicity_id.auth_user.first_name if obj.publicity_id else 'N/A',
            obj.publicity_id.auth_user.last_name if obj.publicity_id else 'N/A',
            obj.publicity_id.publicity_name if obj.publicity_id else 'N/A',
            '',  # Espacio reservado para la imagen de publicidad
            obj.publicity_id.days_transmit if obj.publicity_id else 'N/A',
            str(obj.sending_day),
            obj.reference_number,
            '',  # Espacio reservado para la imagen de captura de pago
            obj.payment_status
        ]
        ws.append(row_data)

        # Insertar imagen de publicidad
        if obj.publicity_id and obj.publicity_id.publicity:
            img = PilImage.open(obj.publicity_id.publicity.path)
            resized_img = resize_image(img, max_img_width, max_img_height)
            img_io = io.BytesIO()
            resized_img.save(img_io, format='PNG')
            img_io.seek(0)
            excel_img = ExcelImage(img_io)
            ws.add_image(excel_img, f'E{row_num}')  # Colocar la imagen en la columna E

        # Insertar imagen de captura de pago
        if obj.payment_proof:
            img = PilImage.open(obj.payment_proof.path)
            resized_img = resize_image(img, max_img_width, max_img_height)
            img_io = io.BytesIO()
            resized_img.save(img_io, format='PNG')
            img_io.seek(0)
            excel_img = ExcelImage(img_io)
            ws.add_image(excel_img, f'I{row_num}')  # Colocar la imagen en la columna I

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Datos_de_Pagos_{timezone.now().strftime("%Y%m%d%H%M%S")}.xlsx'
    
    wb.save(response)
    return response

class PaymentResource(resources.ModelResource):
    # Definir campos personalizados para exportación
    auth_user = fields.Field(attribute='publicity_id__auth_user__id', column_name='ID de Usuario')
    first_name = fields.Field(attribute='publicity_id__auth_user__first_name', column_name='Nombre')
    last_name = fields.Field(attribute='publicity_id__auth_user__last_name', column_name='Apellido')
    publicity_name = fields.Field(attribute='publicity_id__publicity_name', column_name='Nombre de Publicidad')
    publicity = fields.Field(attribute='publicity_id__publicity', column_name='Publicidad')
    days_transmit = fields.Field(attribute='publicity_id__days_transmit', column_name='Dias De Trasnmision')
    sending_day = fields.Field(column_name='Fecha de Pago')
    reference_number = fields.Field(column_name='Referencia De Pago')
    payment_proof_base64 = fields.Field(column_name='Captura de Pago')
    payment_status = fields.Field(column_name='Estado de Pago')

    class Meta:
        model = Payment
        fields = (
            'auth_user',
            'first_name',
            'last_name',
            'publicity_name',
            'publicity_image_base64',  # Campo personalizado para la imagen en base64
            'days_transmit',
            'sending_day',
            'reference_number',
            'payment_proof_base64',  # Campo personalizado para la imagen en base64
            'payment_status'
        )
        export_order = fields  # Opcional: Define el orden de exportación

    def get_queryset(self):
        # Optimizamos las consultas utilizando select_related
        return super().get_queryset().select_related('publicity_id')

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

    # def changelist_view(self, request, extra_context=None):
    #     # Verifica si no hay ningún parámetro GET aplicado y si la sesión no tiene la bandera 'has_redirected'
    #     print('entro')
    #     if not request.GET and not request.session.get('has_redirected', False):
    #         print('redirect')
    #         # Marca en la sesión que ya se ha hecho la redirección
    #         request.session['has_redirected'] = True
    #         # Redirige a "Pending"
    #         return redirect(f"{request.path}?payment_status__exact=pending")
    #     # Si hay un filtro aplicado o es una visita posterior, no redirige y muestra los resultados filtrados
    #     response = super().changelist_view(request, extra_context=extra_context)
    #     # Resetea la bandera si se han aplicado filtros
    #     if request.GET :
    #         print(request.GET['payment_status__exact'])
    #         print('ultimo if')
    #         request.session['has_redirected'] = False
    #     return response
    
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
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('publicity_id').filter(publicity_id__review_result='accepted')
        return queryset

    # Sobrescribir el método export_action
    def export_action(self, request, *args, **kwargs):
        # Obtener el queryset
        queryset = self.get_queryset(request)
        
        # Llamar a la función export_with_images
        return export_with_images(queryset)

class DataUserResource(resources.ModelResource):
    # Definir campos personalizados para exportación
    username = fields.Field(attribute='auth_user__username', column_name='Nombre de Usuario')
    first_name = fields.Field(attribute='auth_user__first_name', column_name='Nombre')
    last_name = fields.Field(attribute='auth_user__last_name', column_name='Apellido')
    last_login = fields.Field(attribute='auth_user__last_login', column_name='Ultimo Inicio de Sesión')
    email = fields.Field(attribute='auth_user__email', column_name='Correo')
    date_joined = fields.Field(attribute='auth_user__date_joined', column_name='Fecha de Registro')
    is_active = fields.Field(attribute='auth_user__is_active', column_name='Estado de Usuario')
    phone = fields.Field(column_name='Numero de Telefono')
    sector = fields.Field(column_name='Sector de vivienda')
    
    class Meta:
        model = DataUser
        fields = (
            'auth_user',
            'username', 
            'date_joined',
            'first_name', 
            'last_name', 
            'last_login', 
            'email', 
            'phone', 
            'sector', 
            'is_active'
            
        )
        export_order = fields  # Opcional: Define el orden de exportación

    def get_queryset(self):
        # Optimizamos las consultas utilizando select_related
        return super().get_queryset().select_related('auth_user')

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
        queryset = super().get_queryset(request)
        return queryset.select_related('auth_user')

    def export_action(self, request, *args, **kwargs):
        # Especificamos el formato (puedes cambiarlo si prefieres otro formato)
        export_format = XLSX()

        # Obtenemos el recurso de la clase directamente
        resource = self.resource_class()

        # Obtenemos el queryset
        queryset = self.get_queryset(request)
        
        # Exportamos el dataset
        dataset = resource.export(queryset)
        
        # Preparamos la respuesta con el archivo a exportar
        response = HttpResponse(
            export_format.export_data(dataset),
            content_type=export_format.get_content_type()
        )
        response['Content-Disposition'] = f'attachment; filename=Datos_de_Usuarios_{timezone.now()}.{export_format.get_extension()}'
        return response