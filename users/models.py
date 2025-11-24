from django.contrib.auth.models import AbstractUser # 👈 AbstractUser를 import
from django.db import models
from shop import models as shop_models

class User(AbstractUser):
    avatar = models.ImageField(null=True, blank=True)
    name = models.CharField(max_length=10, default="", blank=True)
    eng_name = models.TextField(default="", blank=True)
    info = models.TextField(default="", blank=True)
    email = models.EmailField(unique=True) 
    tel = models.CharField(max_length=11, default="", blank=True)
    birthday = models.CharField(max_length=10, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    detail_address = models.CharField(max_length=255, blank=True, null=True)
    extra_address = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'  # username 대신 email을 고유 필드로 사용
    REQUIRED_FIELDS = ['username']  # 다른 필드에 username도 필요하면 추가

    def __str__(self):
        return self.email
# Create your models here.
