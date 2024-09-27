from django.shortcuts import render, redirect
from django.contrib.auth import logout as logout_method, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User

# Modulos propios de la app
from .models import Publicity, Payment, TransmissionDay, DataUser
from .utils import generate_unique_name, register, get_images_user, save_puclicity, send_emails, confirm_email
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
            
            # Se realiza el proceso de confirmación de correo.
            if new_user['status']:
                confirm_email(request, new_user['new_user'])
                
                return redirect('mavi:register_done')
            else:
                return render(request, 'login_register/login_register.html')
        
        # Si los datos no son suficiente para un registro se inicia sesion.
        else:   
            
            try:
                user = User.objects.get(username=cd['user'][0])
            except User.DoesNotExist:
                user = None
            
            
            if user is not None:
                # Verificar si la cuenta está inactiva
                if not user.is_active:
                    messages.error(request, "Tu cuenta está inactiva. Por favor, verifica tu correo para activarla.")
                    confirm_email(request, user)
                    return render(request, 'login_register/register_done.html')

                # Verificar credenciales ingresadas con correo
                user = authenticate(request, username= cd['user'][0], password=cd['password'][0])

            # Si estan validos lo loguea y redirige a index
            if user != None:
                login(request, user)
                return redirect('/dashboard')
            
            # Si es incorrecto envia un mensaje de error y lo manda nuevamente al inicio de seccion
            else:
                messages.error(request, message.LOGIN_ERROR_MESSAGE)
                return render(request, 'login_register/login_register.html')
        
    # Si hace peticiones via get
    else:
        return render(request, 'login_register/login_register.html')    
        
        
def register_done_viewes(request):
    return render(request, 'login_register/register_done.html')
    

def activate_account_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # Activar el usuario
        user.is_active = True
        user.save()

        # Iniciar sesión automáticamente
        login(request, user)

        # Redirigir al dashboard
        messages.success(request, message.REGISTRATION_SUCCESS_MESSAGE)
        return redirect('/dashboard')
    else:
        # Si el token es inválido
        messages.error(request, "El enlace de activación no es válido o ha expirado.")
        return render(request, 'login_register/login_register.html')


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
                send_emails(request, user, url_name='mavi:password_reset_confirm', email_template='password_reset/password_reset_email.html')

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

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DataUser

@login_required
def profile(request):
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.POST.get('email')
        sector = request.POST.get('sector')
        operator_code = request.POST.get('operator_code')
        phone = request.POST.get('phone')

        # Validar que se han enviado todos los datos necesarios
        if not email or not sector or not operator_code or not phone:
            messages.error(request, message.PROFILE_UPDATE_REQUIRED_FIELDS_ERROR_MESSAGE)
            return redirect('mavi:profile')  # Redirigir a la misma página si hay un error

        # Obtener el usuario actual
        user = request.user
        changes_made = False  # Variable para verificar si se han realizado cambios

        # Actualizar el email si ha cambiado
        if user.email != email:
            user.email = email
            changes_made = True  # Se realizó un cambio
            user.save()

        # Concatenar el código del operador con el teléfono
        full_phone = f"{operator_code}{phone}"

        # Actualizar el modelo DataUser
        try:
            data_user = DataUser.objects.get(auth_user=user)
            if data_user.sector != sector:
                data_user.sector = sector
                changes_made = True  # Se realizó un cambio

            if data_user.phone != full_phone:
                data_user.phone = full_phone
                changes_made = True  # Se realizó un cambio

            data_user.save()
        except DataUser.DoesNotExist:
            messages.error(request, message.PROFILE_UPDATE_NOT_FOUND_ERROR_MESSAGE)
            return redirect('mavi:profile')

        # Mostrar mensaje de éxito solo si se realizaron cambios
        if changes_made:
            messages.success(request, message.PROFILE_UPDATE_SUCCESS_MESSAGE)

        return redirect('mavi:profile')

    else:
        # Enviar los datos actuales del usuario a la plantilla
        try:
            user_data = DataUser.objects.get(auth_user=request.user)
        except DataUser.DoesNotExist:
            user_data = None

        return render(request, 'profile/profile.html', {'user': user_data})



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
        advertising_image = request.FILES['publicity']
        # Se obtienen el resto de datos
        cd = dict(request.POST)
        
        save_puclicity(cd, advertising_image, request.user)

        messages.success(request, message.PUBLICITY_SAVE_SUCCESS_MESSAGE)
        return redirect('/dashboard')
    
    else:
        selected_plan = request.GET.get('plan', 'basic')  # Obtén el parámetro 'plan' de la URL
        return render(request, 'upload_publicity/upload_publicity.html', {'selected_plan': selected_plan})
    
    
def screen(request):
    
    today = timezone.now().date()
    publicity_ids = TransmissionDay.objects.filter(transmission_day=today).values_list('publicity_id', flat=True)
    
    # Extraer todos los registros del modelo Imagenes
    publicities = Publicity.objects.filter(id__in=publicity_ids)

    # renderizar la plantilla adecauada y enviar las rutas de las imagenes 
    return render(request, 'vista/vista.html', {'publicities':publicities})   


# Vista que se encargara de los pagos
@login_required
def payment(request):
    if (request.method == 'POST') and ('payment_proof' in request.FILES):
        payment_proof = request.FILES['payment_proof']
        unique_name = generate_unique_name(payment_proof)
        payment_proof.name = unique_name
        
        try:
            publicity_id = request.POST.get('publicity_id')
            publicity_id = Publicity.objects.get(id=publicity_id)
        except:
            messages.error(message.PAYMENT_SAVE_ERROR_MESSAGE)
            redirect('/dashboard')
            
        reference_number = request.POST['reference_number']
        
        payment = Payment()
        payment.publicity_id = publicity_id
        payment.reference_number = reference_number
        payment.payment_proof = payment_proof
        payment.save()
        
        messages.success(request, message.PAYMENT_SAVE_SUCCESS_MESSAGE)
        return redirect('/dashboard')
        
    else:
        if request.POST.get('publicity_id'):
            publicity_id = request.POST.get('publicity_id')
        return render(request, 'payment/payment.html', {'publicity_id':publicity_id})
        