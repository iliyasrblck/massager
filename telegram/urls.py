from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'telegram'
urlpatterns = [
    path('', views.index_views, name='index'),
    #صفحه چت
    path('chat/<str:username>/', views.privet_chat_views, name='privet_chat'),
    path('chat/<str:username>/block/', views.block_V, name='block_user'),

    #ورود و خروج
    path('login/', views.login_views, name='login'),
    path('logout/', views.logout_views, name='logout'),

    #ثبت نام
    path('signup/', views.signup_views, name='signup'),
    path('signup/otp/', views.check_otp, name='check_otp'),

    #عوض کردن پسورد
    path('reset-password/', views.write_email_RP_views, name='password_reset'),
    path('reset-password/cod/', views.cod_otp_RP_views, name='password_cod'),
    path('reset-password/password/', views.reset_password_views, name='password_change'),
    path('profile/', views.profile_V, name='profile'),
    path('chat/profile/<str:username>/', views.chat_profile_V, name='chat_profile'),


]
