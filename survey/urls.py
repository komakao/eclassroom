from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('pre_survey/', views.pre_survey),
    path('post_survey/', views.post_survey),  
    path('pre_result/<int:classroom_id>/', views.pre_result),
    path('post_result/<int:classroom_id>/', views.post_result),  
    path('pre_survey/teacher/<int:classroom_id>/', views.pre_teacher),  
    path('post_survey/teacher/<int:classroom_id>/', views.post_teacher),    
]