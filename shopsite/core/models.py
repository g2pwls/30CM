from django.utils import timezone
from django.db import models

class TimeStampedModel(models.Model): # 👈 다른 모델에서 사용되어질 Abstract Model입니다:)
    """Time Stamped Definition"""
    created = models.DateField(auto_now_add=True, null=True) # 👈 다른 모델에서 공통적으로 사용할 필드
    updated = models.DateField(auto_now=True) # 👈 다른 모델에서 공통적으로 사용할 필드
    class Meta: 
        abstract = True
# Create your models here.
