from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# Modulos propios de la app
from .models import DatosUsuarios, Imagenes
from .utils import registrate, auntenticate


#***************** Vistas que no nececitan iniciar sesion. *****************# 

def index(request):
    return render(request, 'index.html')


# Vista de inicio de seccion y registro.
def iniciar_sesion_registrarse(request):
    if request.method == 'POST':
        
        # Extraer datos del formulario.
        cd = dict(request.POST)

        # Si los datos son suficiente para un registro.
        if 'registrarce' in cd:
            
            # Registrar al usuario nuevo sin usuario.
            nuevo_usuario = registrate(request, cd)
            
            # Se renderiza login_registro.html con un mensaje que indica si fue exitoso o no el registro.
            if nuevo_usuario['estado']:
                return render(request, 'login_registro/login_registro.html', {'mensaje':nuevo_usuario['mensaje']})
        
            else:
                return render(request, 'login_registro/login_registro.html', {'mensaje':nuevo_usuario['mensaje']})
        
        # Si los datos no son suficiente para un registro se inicia sesion.
        else:    
            # Verificar credenciales ingresadas con correo
            # usuario = auntenticate(request, correo= cd['correo'][0], contraseña=cd['contraseña'][0])
            # Verificar credenciales ingresadas con usuario
            usuario = authenticate(request, username= cd['usuario'][0], password=cd['contraseña'][0])

            # Si estan validos lo loguea y redirige a index
            if usuario != None:
                login(request, usuario)
                return HttpResponseRedirect('/')
            
            # Si es incorrecto envia un mensaje de error y lo manda nuevamente al inicio de seccion
            else:
                mensaje = 'Usuario o contraseña incorrectos'
                return render(request, 'login_registro/login_registro.html', {'mensaje':mensaje})
        
    # Si hace peticiones via get
    else:
        return render(request, 'login_registro/login_registro.html')    
        

# Vista de los precios o planes.
def planes(request):
    return render(request, 'planes/planes.html')


# Vista de recuperacion dec contraseña.
def recuperar_contraseña(request):
    if request.method == 'POST':
        pass
    
    else:
        return render(request, 'olvido.html')



#***************** Vistas que nececitan iniciar sesion. *****************# 

# Vista para cerrar seccion.
@login_required
def cerrar_sesion(request):
    logout(request)
    return HttpResponseRedirect('/')


# Vista donde se subiran las imagenes.
@login_required
def subir_img(request):
    if request.method ==  'POST':
        
        # Se obtiene la imagen del formulario
        form_imagen = request.FILES['imagen']
        # Se obtienen el resto de datos
        cd = dict(request.POST)
        
        print(cd, '||||', form_imagen)
    else:
        return render(request, 'subir_img/subir_img.html')
    
    
# Vista que reproducira las imagenes
def vista(request):
    
    # Extraer todos los registros del modelo Imagenes
    imagenes = Imagenes.objects.all()
    
    # Crear una lista vacia para guardar las rutas de las imagenes
    rutas_img = []
    
    # for que recorre los registros para sacar todas las imagenes.
    for imagen in imagenes:
        
        # Extraer la ruta de la imagen 
        ruta = imagen.imagen
        
        # Formatear la ruta para que el javascript pueda encontrar correctamente la imagen
        ruta = str(ruta).replace('mavi/static/', '')
        
        # Agregar la ruta formateada a la lista
        rutas_img.append(ruta)
        
    # renderizar la plantilla adecauada y enviar las rutas de las imagenes 
    return render(request, 'vista/vista.html', {'rutas_img':rutas_img})   


# Vista que se encargara de los pagos
def pagos(request):
    if request.method == 'POST':
        pass
    
    else:
        return render(request, 'pago/pago.html')
        