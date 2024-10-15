from django.db import models
from django.utils import timezone
from store.models import Product
from accounts.models import User

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField( max_length=50 , null=True, blank=True)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE ,blank=True ,  null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)