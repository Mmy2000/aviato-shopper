from django import forms
from .models import ReviewRating , Product , ProductImage
from django.forms import ModelForm


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject' , 'review' , 'rating']


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "stock",
            "PRDBrand",
            "category",
            "image",
        )
        

class ProductImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("image",)