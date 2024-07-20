from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone



class DataUser(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    sector = models.TextField()


class Publicity(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE)
    contract_date = models.DateTimeField(default= timezone.now())
    publicity = models.ImageField(upload_to='mavi/static/img')
    publicity_name = models.CharField(max_length=120)
    days_transmit = models.CharField(max_length=3)
    review_result = models.BooleanField()
    removed =  models.BooleanField(default=False)

class TransmissionDay(models.Model):
    publicity_id = models.ForeignKey(Publicity, on_delete=models.CASCADE)   
    transmission_day = models.DateField()
    

class PasswordRecovery(models.Model):
    auth_user = models.ForeignKey(User, on_delete=models.CASCADE) 
    code = models.CharField(max_length=12)
    
           
class Payment(models.Model):
    publicity_id = models.ForeignKey(Publicity, on_delete=models.CASCADE)
    payment_proof = models.ImageField(upload_to='mavi/static/img/captures_comprobantes')
    reference_number = models.CharField(max_length=50)
    sending_day = models.DateTimeField(default= timezone.now())
    payment_status = models.BooleanField(default=False)