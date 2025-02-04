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
    path('dashboard/' , views.dashboard , name="userdashboard" ),
    path('orders/' , views.orders , name="orders" ),
    path('favorite/' , views.favorite , name="favorite" ),
    path('order_detail/<int:order_id>/' , views.order_detail , name="order_detail" ),


    # API
    path('api/register/', api_view.RegisterView.as_view(), name='register-api'),
    path('api/login/', api_view.LoginView.as_view(), name='login-api'),
    path('api/profile/', api_view.ProfileDetailUpdateView.as_view(), name='profile-detail-update-api'),
    path('api/change-password/', api_view.ChangePasswordView.as_view(), name='change-password'),
    path('api/password-reset/', api_view.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('api/password-reset-confirm/', api_view.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/favorites/', api_view.FavoriteProductsView.as_view(), name='favorite-products'),
    path('api/orders/', api_view.UserOrdersView.as_view(), name='user-orders'),
    path('api/orders/<int:order_id>/', api_view.OrderDetailView.as_view(), name='order-detail'),
]
