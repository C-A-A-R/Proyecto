import datetime
from django.db.models import Count
from django.utils import timezone
import os
import uuid
from django.shortcuts import redirect
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
    
    payments = Payment.objects.all()
    
    payments = []
    for publicity in publicities:
        payments.append(Payment.objects.get(id=publicity.id))

    queryset = []


    for publicity, payment in zip(publicities,payments):
        publicity.publicity = str(publicity.publicity).replace('mavi/static/', '')
        
        if payment.reference_number == '' and payment.payment_proof == '':
            publicity.pay = True
            queryset.append(publicity)
            
        elif payment.payment_status == False:
            publicity.pending = True
            queryset.append(publicity)
            
        else:
            queryset.append(publicity)

    return queryset

def reupload_publicity(request, publicity_id):
    # publicity = Publicity.objects.get(id = publicity_id)
    pass


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
        print()
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

    for i in range(days):
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
        publicity.review_result = False
        publicity.removed = False
        publicity.save()
        
        # Se genera una instancia del modelo Payment y se crea un registro.
        payment = Payment()
        payment.publicity_id = publicity
        payment.save()
        

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
        dict: {'message':mensaje, 'estado':bool}
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