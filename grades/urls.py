# create a new url pattern for the grades app that will be used to display the grades
from django.urls import path
# template views are used to display the html pages
from django.views.generic import TemplateView

from grades import views


urlpatterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile, name='profile'),
    path('profile_edit/', views.edit_profile, name='profile_edit'),
    path('grades/', views.grades_add, name='grades_add'),
    # path('statistic/', views.statistic, name='statistic'),
    path('grades/delete/<int:pk>', views.grade_delete, name='grade_delete'),
]

