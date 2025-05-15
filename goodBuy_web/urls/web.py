from django.urls import path
from goodBuy_web.views import *
from goodBuy_web.views.user_login_register import *

urlpatterns = [
    path('', homePage, name='home'),
    path('login/', logins, name='login'),
    path('register/', register, name='register'),
    path('logout/', logouts, name='logout'),
    path('editprofile/', editProfile, name='editprofile'),
]