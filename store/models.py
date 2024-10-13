from django.db import models
import uuid
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User
from category.models import Subcategory 
from decimal import Decimal

# Create your models here.

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=50)
    image = models.ImageField(upload_to='product/')
    stock = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(max_length=10000, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    views = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    PRDBrand = models.ForeignKey('Brand', related_name='product_brand', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Brand")
    like = models.ManyToManyField(User, blank=True, related_name='product_favourite')
    category = models.ForeignKey(Subcategory, related_name='product_subcategory', verbose_name="Subcategory", null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/')

    def __str__(self):
        return str(self.product)