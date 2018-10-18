#accounts/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    phone_number = models.CharField(max_length = 20)
    address = models.CharField(max_length = 50)
#원투원필드 지정해주고 지금 phone_number, address 유저 필드 추가