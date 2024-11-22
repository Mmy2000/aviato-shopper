from django.urls import path

from settings.api_view import ContactUsView, NewsletterView
from . import views

urlpatterns = [
    path('' , views.home , name='home'),
    
    # API
    path('contact/', ContactUsView.as_view(), name='contact_us'),
    path('newsletter/', NewsletterView.as_view(), name='newsletter'),
]