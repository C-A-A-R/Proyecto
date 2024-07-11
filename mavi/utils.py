from django.shortcuts import render
from django.contrib.auth.models import User
from .models import DataUser


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