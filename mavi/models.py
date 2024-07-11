from django.db import models
from django.contrib.auth.models import User 
from django.utils.timezone import now



class DataUser(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    sector = models.TextField()


class Imagenes(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_de_contrato = models.DateTimeField(default= now())
    modo = models.BooleanField(default=False)
    imagenes = models.ImageField(upload_to='mavi/static/img')
    

class DiasDeTrasmiciones(models.Model):
    imagen = models.ForeignKey(Imagenes, on_delete=models.CASCADE)   
    dia_de_trasmicion = models.DateField()
    

class RecuperarContraseña(models.Model):
      auth_user = models.ForeignKey(User, on_delete=models.CASCADE) 
      codigo = models.CharField(max_length=12)
      
           
class Pagos(models.Model):
    imagenesID = models.ForeignKey(Imagenes, on_delete=models.CASCADE)
    capture_comprobante = models.ImageField(upload_to='mavi/static/img/captures_comprobantes')
    numero_de_referencia = models.CharField(max_length=50)
    dia_de_envio = models.DateTimeField(default= now())
