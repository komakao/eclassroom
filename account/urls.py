from django.urls import path
from . import views
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('dashboard/<int:action>/',  views.MessageList.as_view()),
    path('login/<int:role>', views.Login.as_view()),
    path('logout/', views.Logout.as_view()),  
    path('user/<int:group>', views.UserList.as_view()),
    path('user/create/', views.UserCreate.as_view()),    
    path('user/detail/<int:user_id>', views.account_detail),
    path('user/<int:pk>/update/', views.UserUpdate.as_view()), 
    path('user/<int:pk>/password/', views.UserPasswordUpdate.as_view()), 
    path('user/<int:pk>/teacher/', views.UserTeacher.as_view()),    	
    #設定教師
    path('teacher/make/', views.make),  	
    # 私訊
    path('line/', views.LineListView.as_view()),    
    path('line/class/<int:classroom_id>/', views.LineClassListView.as_view()),        
    path('line/add/<int:classroom_id>/<int:user_id>/', views.LineCreateView.as_view()),
    path('line/reply/<int:classroom_id>/<int:user_id>/<int:message_id>/', views.LineReplyView.as_view()),	
    path('line/detail/<int:classroom_id>/<int:message_id>/', views.line_detail),
	path('line/download/<int:file_id>/', views.line_download), 
	path('line/showpic/<int:file_id>/', views.line_showpic),
    # 列所出有圖像
    path('avatar/', views.avatar),  	
    #修改暱稱
    path('adminname/<int:user_id>/', views.adminnickname),    
    path('nickname/<int:user_id>/<int:classroom_id>/', views.nickname), 	
    # 讀取訊息
    path('message/<int:messagepoll_id>/', views.message),	
    #修改密碼
    #path('password-change/', views.password_self),
    #path('password-change/done/', auth_views.password_change_done),    
    path('password/<int:user_id>/<int:classroom_id>/', views.password),	
    #訪客
    path('statics/login/', views.VisitorListView.as_view()),    
    path('statics/login/log/<int:visitor_id>/', views.VisitorLogListView.as_view()),  	
] 