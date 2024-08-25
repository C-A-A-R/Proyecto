import copy
import datetime
from django.db.models import Count
from django.utils import timezone
import os
import uuid
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import DataUser, Publicity, Payment, TransmissionDay


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
        publicity.publicity = str(publicity.publicity).replace('mavi/static/', '')
            
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
            queryset.append(publicity)

    return queryset

def reupload_publicity(request, publicity_id):
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
    messages.success(request, 'La publicidad ha sido re-subida correctamente.')
    
    return redirect('/dashboard')

def delete_publicity(request, publicity_id):
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
    
    hoy = timezone.now().date()

    # Realizar la consulta para encontrar el primer día disponible
    day_available = (TransmissionDay.objects
                      .filter(transmission_day__gte=hoy)
                      .values('transmission_day')
                      .annotate(total=Count('id'))
                      .filter(total__lt=30)
                      .order_by('transmission_day')
                      .first())

    if day_available:
        return day_available['transmission_day']
    
    else:
        return hoy  # Si no se encuentra ningún día disponible, devolver hoy


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
    


def save_puclicity(cd, form_publicity, user_id):
    # Generar un nombre de archivo único para la publicidad
        unique_name = generate_unique_name(form_publicity)
        form_publicity.name = unique_name
        
        # Se genera una instancia del modelo Publicity y se crea un registro.
        publicity = Publicity() 
        publicity.auth_user = user_id
        publicity.publicity = form_publicity
        publicity.publicity_name = cd['name'][0]
        publicity.days_transmit = cd['days'][0]
        publicity.removed = False
        publicity.save()


def auntenticate(request, correo, contraseña):
    """Funcion que auntentifica las credenciales del usuario, usando request, correo y contraseña.

    Args:
        request (request): El request de la vista.
        correo (str): Correo al que se le desea iniciar la sesión.
        contrase (str): Contraseña afiliada al usuario del correo

    Returns:
        dict: {'mensaje':mensaje, 'estado':bool}
    """
    user = User.objects.filter(email=correo).exists()
    if user:
        user = User.objects.get(email=correo)
        if user.password == contraseña:
            request.session['id'] = user.id
            
        else:
            return {'message':'La contraseña es incorrecta.', 'estado':True}
    else:
        return {'message':'El correo es invalido.', 'estado':False}


def register(request, cd):
    """Funcion que registra al usuario guardando sus datos en el modelo de User de django.

    Args:
        request (request): El request de la vista.
        cd (dict): diccionario que contiene los datos necesarios para el registro

    Returns:
        dict: {'message':mensaje, 'status':bool}
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
            new_user.is_active = True
            new_user.save()
            
            datos_nuevo_usuario = DataUser()
            datos_nuevo_usuario.auth_user = new_user
            datos_nuevo_usuario.sector = cd['sector'][0]
            datos_nuevo_usuario.phone = cd['phone'][0]
            datos_nuevo_usuario.save()
            
            message = '!A sido registrado exitosamente¡'
            return {'message':message, 'status':True}
            
        # Indicar que el usuario o el email ya existe
    else:
            error = 'Este correo ya existe por farvor intentelo de nuevo.'
            return {'message':error, 'status':False}