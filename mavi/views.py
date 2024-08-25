from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth import logout as logout_method, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.html import strip_tags
from django.contrib.auth.models import User

# Modulos propios de la app
from .models import DataUser, Publicity, Payment, TransmissionDay
from .utils import generate_unique_name, register, auntenticate, get_images_user, save_puclicity
from . import message

#***************** Vistas que no nececitan iniciar sesion. *****************# 

def index(request):
    return render(request, 'index/index.html')


# Vista de inicio de seccion y registro.
def login_register(request):
    if request.method == 'POST':
        # Extraer datos del formulario.
        cd = dict(request.POST)

        # Si los datos son suficiente para un registro.
        if 'register' in cd:
            # Registrar al usuario nuevo sin usuario.
            new_user = register(request, cd)
            
            # Se renderiza login_registro.html con un mensaje que indica si fue exitoso o no el registro.
            if new_user['status']:
                messages.success(request, message.REGISTRATION_SUCCESS_MESSAGE)
                return render(request, 'login_registro/login_registro.html')
        
            else:
                return render(request, 'login_registro/login_registro.html')
        
        # Si los datos no son suficiente para un registro se inicia sesion.
        else:    
            # Verificar credenciales ingresadas con correo
            user = authenticate(request, username= cd['user'][0], password=cd['password'][0])

            # Si estan validos lo loguea y redirige a index
            if user != None:
                login(request, user)
                return redirect('/dashboard')
            
            # Si es incorrecto envia un mensaje de error y lo manda nuevamente al inicio de seccion
            else:
                messages.error(request, message.LOGIN_ERROR_MESSAGE)
                return render(request, 'login_registro/login_registro.html')
        
    # Si hace peticiones via get
    else:
        return render(request, 'login_registro/login_registro.html')    
        

# Vista de los precios o planes.
def plans(request):
    return render(request, 'plans/plans.html')


#***************** Vistas de recuperacion de contraseña. *****************#
def password_reset_request_view(request):
    if request.method == "POST":
            email = request.POST['email']
            users = User.objects.filter(email=email)
            if users.exists():
                user = users[0]
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_link = request.build_absolute_uri(
                    reverse('mavi:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )

                # Renderizar la plantilla HTML con el contexto
                mail_subject = 'Restablecimiento de contraseña solicitado'
                html_message = render_to_string('password_reset/password_reset_email.html', {
                    'user': user,
                    'reset_link': reset_link,
                })
                plain_message = strip_tags(html_message)  # Mensaje en texto plano como alternativa
                from_email = 'aragozaca@gmail.com'
                to_email = [user.email]

                # Enviar el correo
                send_mail(mail_subject, plain_message, from_email, to_email, html_message=html_message)

                return redirect('mavi:password_reset_done')
    else:
        return render(request, 'password_reset/password_reset_form.html')

            
def password_reset_confirm_view(request, uidb64=None, token=None):
    if uidb64 is None or token is None:
        return redirect('mavi:password_reset_request')

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            cd = dict(request.POST)
            if cd['password1'][0] == cd['password2'][0]:
                user.set_password(cd['password1'][0])
                user.save()
                return redirect('mavi:login_register')
            else:
                messages.error(message.PASSWORD_RESET_VALIDATION_ERROR_MESSAGE)
                return render(request, 'password_reset/password_reset_confirm.html')
    else:        
        messages.error(message.PASSWORD_RESET_TOKEN_ERROR_MESSAGE)
        return redirect('mavi:password_reset_request')

    return render(request, 'password_reset/password_reset_confirm.html')
                
                
def password_reset_done_view(request):
    return render(request, 'password_reset/password_reset_done.html')



#***************** Vistas que nececitan iniciar sesion. *****************# 

@login_required
def dashboard(request):
    user_id = request.user.id
    images = get_images_user(user_id)
    return render(request, 'dashboard/dashboard.html', {'images':images})


# Vista para cerrar seccion.
@login_required
def logout(request):
    logout_method(request)
    return redirect('/')


# Vista donde se subiran las imagenes.
@login_required
def upload_publicity(request):
    if request.method ==  'POST':
        
        # Se obtiene la imagen del formulario
        form_publicity = request.FILES['publicity']
        # Se obtienen el resto de datos
        cd = dict(request.POST)
        
        save_puclicity(cd, form_publicity, request.user)

        messages.success(request, message.PUBLICITY_SAVE_SUCCESS_MESSAGE)
        return redirect('/dashboard')
    
    else:
        selected_plan = request.GET.get('plan', 'basic')  # Obtén el parámetro 'plan' de la URL
        return render(request, 'upload_publicity/upload_publicity.html', {'selected_plan': selected_plan})
    
    
def screen(request):
    
    today = timezone.now().date()
    publicity_ids = TransmissionDay.objects.filter(transmission_day=today).values_list('publicity_id', flat=True)
    
    # Extraer todos los registros del modelo Imagenes
    publicity = Publicity.objects.filter(id=publicity_ids)
    
    # Crear una lista vacia para guardar las rutas de las imagenes
    rutas_publicity = []
    
    # for que recorre los registros para sacar todas las imagenes.
    for imagen in publicity:
        
        # Extraer la ruta de la imagen 
        ruta = imagen.publicity
        
        # Formatear la ruta para que el javascript pueda encontrar correctamente la imagen
        ruta = str(ruta).replace('admin_app/static/', '')
        # Agregar la ruta formateada a la lista
        rutas_publicity.append(ruta)
        
    # renderizar la plantilla adecauada y enviar las rutas de las imagenes 
    return render(request, 'vista/vista.html', {'rutas_img':rutas_publicity})   


# Vista que se encargara de los pagos
@login_required
def payment(request):
    if request.method == 'POST':
        payment_proof = request.FILES['payment_proof']
        unique_name = generate_unique_name(payment_proof)
        payment_proof.name = unique_name
        
        publicity_id = request.POST.get('publicity_id')
        publicity_id = Publicity.objects.get(id=publicity_id)
        
        reference_number = request.POST['reference_number']
        
        payment = Payment()
        payment.publicity_id = publicity_id
        payment.reference_number = reference_number
        payment.payment_proof = payment_proof
        payment.save()
        
        messages.success(request, message.PAYMENT_SAVE_SUCCESS_MESSAGE)
        return redirect('/dashboard')
        
    else:
        return render(request, 'payment/payment.html')
        