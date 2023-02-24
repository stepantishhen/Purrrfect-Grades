# create a new url pattern for the grades app that will be used to display the grades
from django.urls import path

from grades import views

urlpatterns = [
    path('', views.index, name='index'),
]

