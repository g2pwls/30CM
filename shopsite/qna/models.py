from django.db import models
# notice/models.py

import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from shop.models import Product

class QnaCategory(models.Model):
    qna_name = models.CharField(max_length=50, unique=True)  # name에서 qna_name으로 변경
    qna_slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)  # slug에서 qna_slug로 변경

    def __str__(self):
        return self.qna_name  # 변경된 qna_name 사용

    def get_absolute_url(self):
        return reverse('qna:index', args=[self.qna_name])  # 변경된 qna_name 사용

    class Meta:
        verbose_name_plural = 'qnacategories'


class Qna(models.Model):
    category = models.ForeignKey(QnaCategory, null=True, blank=True, on_delete=models.SET_NULL)
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='작성자')
    title = models.CharField(max_length=128, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성 시각')  # 생성 시 자동으로 시간 기록
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정 시각')      # 수정 시 자동으로 시간 기록
    is_private = models.BooleanField(default=False)

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="qnas")

    def __str__(self):
        return self.title

class Reply(models.Model):
    content = models.TextField()
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    qna = models.OneToOneField(Qna, on_delete=models.CASCADE, related_name="reply")  # Qna와 1:1 관계 설정
    created_at = models.DateTimeField(auto_now_add=True)