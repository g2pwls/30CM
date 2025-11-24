import uuid
from django.conf import settings
from django.db import models
from users import models as user_models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from shop import models as shop_models
from core import models as core_models
from users import models as users_models

 
class Payment(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    imp_uid = models.CharField(max_length=100, unique=True)  # 아임포트 결제 고유번호
    merchant_uid = models.CharField(max_length=100, null=True, blank=True, unique=True, default=uuid.uuid4)  # 주문번호
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.merchant_uid} - {self.amount}원"
    
class ColorCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:index', args=[self.name])
    
    class Meta:
        verbose_name_plural = 'Colorcategories'

class SizeCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:index', args=[self.name])

    class Meta:
        verbose_name_plural = 'Sizecategories'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_category', args=[self.slug])
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="subcategories")
    name = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index= True, unique= True)


    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_category', args=[self.category.slug, self.slug])
    
    class Meta:
        ordering = ['name']


class NestedSubCategory(models.Model):
    parent_subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="nested_subcategories")
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('shop:product_category',         args=[
            self.parent_subcategory.category.slug, 
            self.parent_subcategory.slug, 
            self.slug
        ])
    
    class Meta:
        ordering = ['name']  # 이름 순으로 정렬

class Product(core_models.TimeStampedModel):

    id = models.AutoField(primary_key=True)
    #상품 아이디

    name = models.CharField(max_length=200)

    price = models.IntegerField(max_length=200)

    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)

    subcategory = models.ForeignKey(SubCategory, null=True, blank=True, on_delete=models.SET_NULL)

    nested_subcategory = models.ForeignKey(NestedSubCategory, null=True, blank=True, on_delete=models.SET_NULL)

    head_image = models.ImageField(upload_to='shop/images/%Y/%m/%d/', blank=True)

    image = models.ImageField(upload_to='shop/images', blank=False)

    size = models.ForeignKey(SizeCategory, null=True, blank=True, on_delete=models.SET_NULL)

    color = models.ForeignKey(ColorCategory, null=True, blank=True, on_delete=models.SET_NULL)


    host = models.ForeignKey("users.User", on_delete=models.CASCADE)

    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    def is_in_stock(self):
        return self.stock > 0
    
    def like_count(self):
        return self.likes.count()
    
    def has_liked(self, user):
        """해당 사용자가 좋아요를 눌렀는지 확인"""
        if user.is_authenticated:
            return Like.objects.filter(product=self, user=user).exists()
        return False

    
class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="like_products")
    product = models.ForeignKey(Product, related_name="likes", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # 각 사용자-상품 쌍에 대해 한 번만 좋아요 가능

    def __str__(self):
        return f"{self.user} likes {self.product}"
