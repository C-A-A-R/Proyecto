from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone



class DataUser(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='numero telefonico')
    sector = models.TextField()

    def __str__(self):
            return self.auth_user.username
        
    class Meta:
            verbose_name = "Dato de Usuario"
            verbose_name_plural = "Datos de Usuarios"


class Publicity(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract_date = models.DateTimeField(default= timezone.now(), verbose_name='fecha de subida')
    publicity = models.ImageField(upload_to='advertisements',verbose_name='Publicidad')
    publicity_name = models.CharField(max_length=120,  verbose_name='Nombre de Publicidad')
    days_transmit = models.CharField(max_length=3, verbose_name='dias de transmición')
    review_result = models.CharField(max_length=10, choices=[('pending', 'Pendiente'),('accepted', 'Aceptado'),('rejected', 'Rechazado'),], default='pending', verbose_name='estado')
    removed =  models.BooleanField(default=False)
    
    def __str__(self) :
        return self.publicity_name

    class Meta:
        verbose_name = "Publicidad"
        verbose_name_plural = "Publicidades"



class TransmissionDay(models.Model):
    publicity_id = models.ForeignKey(Publicity, on_delete=models.CASCADE)   
    transmission_day = models.DateField(verbose_name='dias de trasmición')
    
    class Meta:
        verbose_name = "Dia de Trasmición'"
        verbose_name_plural = "Dias de Trasmición'"
    

class Payment(models.Model):
    publicity_id = models.ForeignKey(Publicity, on_delete=models.CASCADE)
    payment_proof = models.ImageField(upload_to='payments',verbose_name='captura de pago')
    reference_number = models.CharField(max_length=50, verbose_name='referencia de pago')
    sending_day = models.DateTimeField(default= timezone.now(), verbose_name='feachade pago')
    payment_status = models.CharField(max_length=10, choices=[('pending', 'Pendiente'),('confirmed', 'Confirmado'),('rejected', 'Rechazado'),], default='pending', verbose_name='Estado')

    def save(self, *args, **kwargs):
        # Llamar a la funcion encargada para agendar la publicidad.
        from .utils import schedule_publicity
        
        # Verifica si el pago está siendo confirmado
        if self.pk:  # Verifica si el objeto ya existe en la base de datos
            old_payment = Payment.objects.get(pk=self.pk)
            if old_payment.payment_status != 'confirmed' and self.payment_status == 'confirmed':
                
                # Aquí llamas a la función para agendar los días de publicación
                schedule_publicity(self.publicity_id, self.publicity_id.days_transmit)
        
        # Llama al método save original para guardar el objeto en la base de datos
        super(Payment, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.publicity_id.publicity_name

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"