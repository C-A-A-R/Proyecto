from django.shortcuts import render
from django.contrib.auth.models import User
from .models import DatosUsuarios


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
            return {'mensaje':'La contraseña es incorrecta.', 'estado':True}
    else:
        return {'mensaje':'El correo es invalido.', 'estado':False}
    
    
def registrate(request, cd):
    """Funcion que registra al usuario guardando sus datos en el modelo de User de django.

    Args:
        request (request): El request de la vista.
        cd (dict): diccionario que contiene los datos necesarios para el registro

    Returns:
        dict: {'mensaje':mensaje, 'estado':bool}
    """
    # Verificar si ya hay un email y correo igual
    usuario = User.objects.filter(username=cd['usuario'][0]).exists()
    correo = User.objects.filter(email=cd['correo'][0]).exists()
     
    # Guardar o registrar al nuevo usuario.
    if not usuario and not correo :
            nuevo_usuario = User()
            nuevo_usuario.username = cd['usuario'][0]
            nuevo_usuario.set_password(cd['contraseña'][0])
            nuevo_usuario.first_name = cd['nombre'][0]
            nuevo_usuario.last_name = cd['apellido'][0]
            nuevo_usuario.email = cd['correo'][0]
            nuevo_usuario.is_active = True
            nuevo_usuario.save()
            
            datos_nuevo_usuario = DatosUsuarios()
            datos_nuevo_usuario.auth_user = nuevo_usuario
            datos_nuevo_usuario.sector = cd['sector'][0]
            datos_nuevo_usuario.telefono = cd['telefono'][0]
            datos_nuevo_usuario.save()
            
            mensaje = '!A sido registrado exitosamente¡'
            return {'mensaje':mensaje, 'estado':True}
            
        # Indicar que el usuario o el email ya existe
    else:
            error = 'Este correo ya existe por farvor intentelo de nuevo.'
            return {'mensaje':error, 'estado':False}