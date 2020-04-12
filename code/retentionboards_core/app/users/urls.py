from django.contrib import admin
from django.urls import path
from django.conf.urls import include, url
from .views import LoginView, LogoutView, RegisterView, MainView

urlpatterns = [
    path('', MainView.as_view()),
    path('login/', LoginView.as_view()),
    path('register/', RegisterView.as_view()),
    path('logout/', LogoutView.as_view()),
        ]