from django.conf import settings
from django.db import models
from shop.models import ColorCategory, Product, SizeCategory

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,null=True, blank=True)
    cart_id = models.CharField(max_length=250, blank=True,unique=True)
    data_added = models.DateField(auto_now_add=True)
    class Meta:
        db_table = 'Cart'
        ordering = ['data_added']

    def __str__(self):
        return self.cart_id
    

class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)
    size = models.ForeignKey(SizeCategory, on_delete=models.SET_NULL, null=True)  # 사이즈
    color = models.ForeignKey(ColorCategory, on_delete=models.SET_NULL, null=True)  # 색상
    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return str(self.product)

# Create your models here.
