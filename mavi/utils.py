import copy
import datetime
from django.db.models import Count
from django.utils import timezone
import os
import uuid
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.html import strip_tags
from django.urls import reverse
from .models import DataUser, Publicity, Payment, TransmissionDay
from .message import PUBLICITY_DELETE_SUCCESS_MESSAGE, PUBLICITY_REUPLOAD_SUCCESS_MESSAGE
from django.utils.timezone import is_aware
from datetime import datetime, timezone


def make_naive(value):
    """
    Si el valor es un objeto datetime con tzinfo, lo convertimos en naive.
    """
    if isinstance(value, datetime) and is_aware(value):
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def get_images_user(user_id):
    """Funcion que obtiene todas las images relacionadas a un usuario teniendo en cuenta 
    el borrado logico.

    Args:
        user_id (id): id del usuario del que se requiere obtener las imagenes

    Returns:
        list: lista con imagenes
    """
    publicities = Publicity.objects.filter(auth_user=user_id, removed=False)
    
    payments = []
    for publicity in publicities:
        if  Payment.objects.filter(publicity_id=publicity.id).exists():
            payments.append(Payment.objects.get(publicity_id=publicity.id))
        else:
            payments.append([])

    queryset = []

    for publicity, payment in zip(publicities,payments):
        publicity.publicity = str(publicity.publicity)
            
        if (publicity.review_result == 'rejected') and (not payment):
            publicity.rejected_image = True
            queryset.append(publicity)
            
        elif (publicity.review_result == 'accepted') and (not payment):
            publicity.pay = True
            queryset.append(publicity)
            
        elif not payment:
            publicity.pending_image = True
            queryset.append(publicity)
            
        elif TransmissionDay.objects.filter(publicity_id=publicity, transmission_day=timezone.now()).exists():
            publicity.transmitting = True
            queryset.append(publicity)
            
        elif payment.payment_status == 'pending':
            publicity.pending_payment = True
            queryset.append(publicity)
            
            
        elif payment.payment_status == 'rejected':
            publicity.rejected_payment = True
            queryset.append(publicity)
            
        else:
            publicity.finished = True
            queryset.append(publicity)

    return queryset


def reupload_publicity(request, publicity_id):
    """Funcion que resube una publicidad.

    Args:
        request (request): Peticion del navegador
        publicity_id (obj): Instancia de la clase publicity

    Returns:
        redirect: Redireccion a dashboard
    """
    publicity = Publicity.objects.get(id = publicity_id)
    # Marca la publicidad original como removida
    publicity.removed = True
    publicity.save()

    # Crear una nueva instancia de Publicity replicando la original
    new_publicity = copy.copy(publicity)  # Realiza una copia superficial del objeto original
    new_publicity.pk = None  # Asegúrate de que la nueva instancia tenga un nuevo ID (nuevo registro)
    
    new_publicity.review_result = 'accepted'  # Establece el nuevo estado de revisión
    new_publicity.removed = False  # Asegúrate de que la nueva publicidad no esté marcada como eliminada
    new_publicity.save()  # Guarda la nueva instancia en la base de datos

    # Agrega un mensaje de éxito
    messages.success(request, PUBLICITY_REUPLOAD_SUCCESS_MESSAGE)
    
    return redirect('/dashboard')


def delete_publicity(request, publicity_id):
    """Funcion que borra logicamente una publicidad.

    Args:
        request (request): Peticion del navegador
        publicity_id (obj): Instancia de la clase publicity

    Returns:
        redirect: Redireccion a dashboard
    """
    messages.success(request, PUBLICITY_DELETE_SUCCESS_MESSAGE)
    Publicity.objects.filter(id=publicity_id).update(removed=True)
    return redirect('/dashboard')


def generate_unique_name(publicity):
    try:
        """
        Genera un nombre de archivo único.

        Args:
            publicity (UploadedFile): Archivo que se le quiera cambiar el nombre.

        Returns:
            str: El nombre de archivo único.
        """
        extension = os.path.splitext(publicity.name)[1]  # Obtener la extensión del archivo
        base_name = os.path.splitext(publicity.name)[0]  # Obtener el nombre base del archivo
        unique_name = f"{uuid.uuid4()}{extension}"  # Generar un nombre único con UUID
        return unique_name
    except Exception as e:
        print(f'A Ocurrido el error "{e}" en la funcion generar_nombre_unico del modulo utils.py')


def find_day_available():
    """Encuentra el primer día disponible a partir de hoy que tiene menos de 30 publicidades
    agendadas.

    Returns:
        date: Fecha del primer día disponible.
    """
    
    today = timezone.now().date()

    # Realizar la consulta para encontrar el primer día disponible
    day_available = (TransmissionDay.objects
                        .filter(transmission_day__gte=today)
                        .values('transmission_day')
                        .annotate(total=Count('id'))
                        .filter(total__lt=30)
                        .order_by('transmission_day')
                        .first()
                    )
    
    if day_available:
        return day_available['transmission_day']
    
    else:
        return today  # Si no se encuentra ningún día disponible, devolver hoy


def schedule_publicity(publicity_id, days):
    """Agenda la publicidad para los próximos 'plan' días asegurando que no haya más de 30
    publicidades por día.

    Args:
        publicity_id (object): Instancia del modelo Publicity..
        days (int): Número de días que la publicidad debe ser transmitida.

    Returns:
        bool: True si se agendó correctamente, False si no fue posible.
    """
    scheduled = False
    extra_days = 0
    day_available = find_day_available()

    for i in range(int(days)):
        while True:
            date = day_available + datetime.timedelta(days=i+extra_days)
            counter = TransmissionDay.objects.filter(transmission_day=date).count()

            if counter < 30:
                TransmissionDay.objects.create(publicity_id=publicity_id, transmission_day=date)
                scheduled = True
                break
            
            else:
                extra_days += 1

    return scheduled
    

def send_emails(request, user, url_name, email_template):
    """Funcion que envia un correo y negera una ruta temporal unica.

    Args:
        request (request): Peticion del navegador.
        user (obj): Instancia de la clase User.
        url_name (str): nombre de la ruta temporal unica 
        email_template (str): template del correo que se enviara.
    """    
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = request.build_absolute_uri(
        reverse(url_name, kwargs={'uidb64': uid, 'token': token})
    )

    # Renderizar la plantilla HTML con el contexto
    mail_subject = 'Restablecimiento de contraseña solicitado'
    html_message = render_to_string(email_template, {
        'user': user,
        'reset_link': reset_link,
    })
    plain_message = strip_tags(html_message)  # Mensaje en texto plano como alternativa
    from_email = 'aragozaca@gmail.com'
    to_email = [user.email]

    # Enviar el correo
    send_mail(mail_subject, plain_message, from_email, to_email, html_message=html_message)


def confirm_email(request, new_user):
    """Funcion que llama a la funcion send_emails y le da los argumetos necesarios para enviar el correo de confirmacion.

    Args:
        request (request): Peticion del navegador.
        new_user (obj): Instancia de la clase User.
    """    
    send_emails(request, new_user, url_name='activate_account', email_template='login_register/register_email.html')


def save_puclicity(cd, advertising_image, user_id):
    """Fucion que guarda la publicidad.

    Args:
        cd (dict): diccionario que contiene los datos necesarios para guardar los datos.
        advertising_image (files): Imagen publicitaria que se esta guardando.
        user_id (_type_): _description_
    """    
    
    # Generar un nombre de archivo único para la publicidad
    unique_name = generate_unique_name(advertising_image)
    advertising_image.name = unique_name
    
    # Se genera una instancia del modelo Publicity y se crea un registro.
    publicity = Publicity() 
    publicity.auth_user = user_id
    publicity.publicity = advertising_image
    publicity.publicity_name = cd['name'][0]
    publicity.days_transmit = cd['days'][0]
    publicity.removed = False
    publicity.save()


def register(cd):
    """Funcion que registra al usuario guardando sus datos en el modelo de User de django.

    Args:
        cd (dict): diccionario que contiene los datos necesarios para el registro

    Returns:
        dict: {'new_user':new_user, message':mensaje, 'status':bool}
    """
    # Verificar si ya hay un email y correo igual
    user = User.objects.filter(username=cd['user'][0]).exists()
    email = User.objects.filter(email=cd['email'][0]).exists()

    # Guardar o registrar al nuevo usuario.
    if not user and not email :
            new_user = User()
            new_user.username = cd['user'][0]
            new_user.set_password(cd['password'][0])
            new_user.first_name = cd['name'][0]
            new_user.last_name = cd['last_name'][0]
            new_user.email = cd['email'][0]
            new_user.is_active = False
            new_user.save()
            
            new_user_data = DataUser()
            new_user_data.auth_user = new_user
            new_user_data.sector = cd['sector'][0]
            new_user_data.phone = cd['phone'][0]
            new_user_data.save()
            
            message = '!A sido registrado exitosamente¡'
            return {'new_user':new_user, 'message':message, 'status':True}
            
        # Indicar que el usuario o el email ya existe
    else:
            error = 'Este correo ya existe por farvor intentelo de nuevo.'
            return {'message':error, 'status':False}