    
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from account import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage),  
    path('account/', include('account.urls')),  
    path('teacher/', include('teacher.urls')), 
    path('student/', include('student.urls')),   
    path('survey/', include('survey.urls')),	
    path('captcha/', include('captcha.urls')),
]
