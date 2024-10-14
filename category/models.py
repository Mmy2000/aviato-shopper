from django.db import models
import uuid

from django.urls import reverse

# Create your models here.

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True,blank=True,upload_to='category-image/')

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']  # Categories will be ordered alphabetically by name.

    def __str__(self):
        return self.name
    
    # Add a method to count the products in this category
    def product_count(self):
        return self.subcategories.aggregate(count=models.Count('product_subcategory'))['count'] or 0

class Subcategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True,blank=True,upload_to='subcategory-image/')

    class Meta:
        verbose_name = "Subcategory"
        verbose_name_plural = "Subcategories"
        ordering = ['name']  # Subcategories will be ordered alphabetically by name.

    def __str__(self):
        return f"{self.category.name} - {self.name}"
    
    def get_url(self):
        return reverse('products_by_subcategory',args=[self.id])
    
    # Add a method to count the products in this subcategory
    def product_count(self):
        return self.product_subcategory.count()