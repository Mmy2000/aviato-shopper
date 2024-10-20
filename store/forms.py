from django import forms
from .models import ReviewRating , Product , ProductImage

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject' , 'review' , 'rating']


class ProductForm(forms.ModelForm):
    class Meta:
        Model = Product
        fields = (
            "name",
            "description",
            "price",
            "stock",
            "PRDBrand",
            "category",
            "image",
        )

class PropertyImagesForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ("image",)