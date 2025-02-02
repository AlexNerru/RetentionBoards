"""RetentionBoards URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from .views import EventsetsView, check_task_status, ExperimentView, GraphView

app_name = 'dashboards'

urlpatterns = [
    path('', EventsetsView.as_view()),
    path('check_status/', check_task_status),
    path('experiments/<int:pk>/', ExperimentView.as_view()),
    path('experiments/<int:pk>/<str:cluster>/', GraphView.as_view()),
    path('csv/', EventsetsView.as_view()),

]