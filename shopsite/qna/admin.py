from django.contrib import admin
from . import models

@admin.register(models.QnaCategory)
class QnaCategoryAdmin(admin.ModelAdmin):
    pass
