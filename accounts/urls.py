from django.urls import path
from . import views
from . import api_view
urlpatterns = [
    path('register/', views.register , name='register' ),
    path('login/', views.login , name='login' ),
    path('logout/', views.logout , name='logout' ),
    path('forgotPassword/', views.forgotPassword, name='forgotPassword'),
    path('resetpassword_validate/<uidb64>/<token>/', views.resetpassword_validate, name='resetpassword_validate'),
    path('resetPassword/', views.resetPassword, name='resetPassword'),
    path('change_password/', views.change_password, name='change_password'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('profile/' , views.profile , name="profile" ),
    path('dashboard/' , views.dashboard , name="dashboard" ),
    path('orders/' , views.orders , name="orders" ),
    path('order_detail/<int:order_id>/' , views.order_detail , name="order_detail" ),


    # API
    path('api/register/', api_view.RegisterView.as_view(), name='register'),
]
