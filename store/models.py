from django.db import models
import uuid
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import User
from category.models import Subcategory 
from decimal import Decimal
from taggit.managers import TaggableManager
from django.db.models import Avg , Count

# Create your models here.

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=50)
    image = models.ImageField(upload_to='product/',null=True,blank=True)
    stock = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    description = models.TextField(max_length=10000, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(null=True, blank=True, unique=True)
    views = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    on_sale = models.BooleanField(default=False)
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

    def avr_review(self):
        reviews = ReviewRating.objects.filter(product=self , status=True).aggregate(average=Avg('rating'))
        avg =0
        if reviews['average'] is not None:
            avg = float(reviews['average'])
        return avg
    
    def count_review(self):
        reviews = ReviewRating.objects.filter(product=self , status=True).aggregate(count=Count('rating'))
        count = 0
        if reviews['count'] is not None:
            count = int(reviews['count'])
        return count

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product/',null=True,blank=True)

    def __str__(self):
        return str(self.product)   
    
class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category='color',is_active=True)
    
    def sizes(self):
        return super(VariationManager,self).filter(variation_category='size',is_active=True)

variation_category_choice=(
    ('color','color'),
    ('size','size'),
)

class Variation(models.Model):
    product = models.ForeignKey(Product,related_name='product_variation',  on_delete=models.CASCADE)
    variation_category = models.CharField( max_length=200 , choices=variation_category_choice)
    variation_value = models.CharField( max_length=200 )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(  auto_now_add=True)
    objects = VariationManager()


    def __str__(self):
        return self.variation_value


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

    def get_url(self):
        return reverse('products_by_brand',args=[self.id])

    def __str__(self):
        return self.name


    
class ReviewRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,related_name='reviewrating', on_delete=models.CASCADE)
    subject = models.CharField(max_length=500 , blank=True)
    review = models.TextField(max_length=500 , blank=True)
    rating = models.FloatField()
    ip = models.CharField( max_length=50 , blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField( auto_now_add=True)
    updated_at = models.DateTimeField( auto_now=True)

    def __str__(self):
        return self.subject