from django.urls import path

from . import views

app_name = 'mavi'


urlpatterns = [
    path('', views.index, name='index'),
    path('inicio_de_sesion/', views.login_register, name='login_register'),
    # path('registro/', views.registro, name='registro'),
    path('recuperar_contraseña/', views.recuperar_contraseña, name='recuperar_contraseña'),
    path('logout/', views.cerrar_sesion, name='cerrar_sesion'),
    path('planes/', views.planes, name='planes'),
    path('subida/', views.subir_img, name='subida'),
    path('pago/', views.pagos, name='pago')
]
