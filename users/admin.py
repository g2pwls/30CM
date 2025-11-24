from django.contrib import admin
from . import models # 👈 해당 model이 존재하는 파일을 import
@admin.register(models.User) # 👈 데코레이터로 등록
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username','name', 'email', 'tel', 'birthday', 'postcode', 'address', 'detail_address', 'extra_address']
    search_fields = ['username','name', 'email', 'tel', 'birthday', 'postcode', 'address', 'detail_address', 'extra_address']
# Register your models here.
