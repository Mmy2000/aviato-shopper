from decimal import Decimal
from django.db import models
from django.utils import timezone
from store.models import Product , Variation
from accounts.models import User

# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=50, null=True, blank=True)
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return self.cart_id


class Tax(models.Model):
    tax = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return str(self.tax)

class CartItem(models.Model):
    user = models.ForeignKey(User,null=True,verbose_name="user cart", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, blank=True, null=True)
    variations = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return str(self.product)
