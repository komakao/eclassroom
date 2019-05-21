# -*- coding: utf8 -*-
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    #班級
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/create/', views.ClassroomCreate.as_view()),    
    path('classroom/<int:pk>/update/', views.ClassroomUpdate.as_view()),
    path('classroom/assistant/<int:classroom_id>/', views.classroom_assistant),
    path('classroom/assistant/add/<int:classroom_id>/<int:group>', views.AssistantListView.as_view()),	
    #列出所有學生帳號
    path('student/list/', views.StudentListView.as_view()),
    #加選學生
    path('student/join/<int:classroom_id>/', views.StudentJoinView.as_view()),	
    path('student/enroll/<int:classroom_id>/', views.StudentEnrollView.as_view()),		
	#大量匯入帳號
    path('import/upload/', views.import_sheet),
    path('import/student/', views.import_student),
    #修改資料
    path('password/<int:user_id>/', views.password),
    path('nickname/<int:user_id>/', views.nickname),
    # 分組
    path('group/<int:classroom_id>/', views.GroupListView.as_view()),
    path('group/add/<int:classroom_id>/', views.GroupCreateView.as_view()),  
    path('group/edit/<int:classroom_id>/<int:pk>/', views.GroupUpdateView.as_view()),    
    path('group/make/', views.make),   
    path('group/make2/<int:group_id>/<int:action>/', views.make2),   
	path('group/assign/<int:classroom_id>/<int:group_id>/', views.group_assign),   
    # 作業
    path('work/<int:classroom_id>/', views.work_list),
    path('work/class/<int:typing>/<int:classroom_id>/<int:index>/', views.work_class),
    path('work/group/<int:typing>/<int:classroom_id>/<int:index>/', views.work_group),
    path('work/group/set/<int:typing>/<int:classroom_id>/', views.work_groupset),    
	path('work/assistant/<int:typing>/<int:classroom_id>/', views.work_assistant),
    #path('work1/<int:lesson>/<int:classroom_id>/', views.work1),	
    # 自訂作業
    path('work2/<int:classroom_id>/', views.work_list2),
    path('work2/add/<int:classroom_id>/', views.WorkCreateView2.as_view()),
    path('work2/edit<int:classroom_id>/', views.work_edit),
    path('work2/class/<int:classroom_id>/<int:work_id>/', views.work_class2),     
    #設定助教	
    path('assistant/', views.AssistantClassroomListView.as_view()),
    path('assistant/make/', views.assistant_make),	
    # 討論區
    #path('forum/<int:categroy>/<int:categroy_id>', views.ForumAllListView.as_view()),  
    #path('forum/show/<int:forum_id>/', views.forum_show), name='forum-show'),    
    path('forum/<int:classroom_id>/', views.ForumListView.as_view()),
    path('forum/add/<int:classroom_id>/', views.ForumCreateView.as_view()),
    path('forum/edit/<int:classroom_id>/<int:pk>/', views.ForumEditUpdate.as_view()),     
    path('forum/class/<int:classroom_id>/<int:forum_id>/', views.ForumClassList.as_view()),      
    path('forum/class/switch/', views.forum_switch),      
    path('forum/deadline/<int:classroom_id>/<int:pk>/', views.ForumDeadlineUpdate.as_view()),  
    path('forum/deadline/set/', views.forum_deadline_set), 
    path('forum/deadline/date/', views.forum_deadline_date),   
    path('forum/content/<int:classroom_id>/<int:forum_id>/', views.ForumContentList.as_view()), 
    path('forum/content/add/<int:classroom_id>/<int:forum_id>/', views.ForumContentCreate.as_view()),
    path('forum/content/delete/<int:classroom_id>/<int:forum_id>/<int:content_id>/', views.forum_delete),   
    path('forum/content/edit/<int:classroom_id>/<int:forum_id>/<int:content_id>/', views.forum_edit),      
    path('forum/download/<int:classroom_id>/<int:content_id>/', views.forum_download),  
    path('forum/export/<int:classroom_id>/<int:forum_id>/', views.forum_export),   
    path('forum/grade/<int:classroom_id>/<int:action>/', views.forum_grade), 	
  	path('forum/publish/reject/<int:classroom_id>/<int:index>/<int:user_id>', views.ForumPublishReject.as_view()),		
	# 問卷區
	path('survey/<int:classroom_id>', views.survey),	
    # 退選
    path('unenroll/<int:enroll_id>/<int:classroom_id>/',views.unenroll),
    #公告
    path('announce/<int:classroom_id>/', views.AnnounceListView.as_view()),
    path('announce/<int:classroom_id>/create', views.AnnounceCreateView.as_view()),
    path('announce/detail/<int:classroom_id>/<int:message_id>/', views.announce_detail),	
    #設定小教師
    path('work/assistant/make/', views.steacher_make),
	#評分
    path('score_peer/<int:typing>/<int:index>/<int:classroom_id>/<int:group>/', views.score_peer),
    path('scoring/<int:typing>/<int:classroom_id>/<int:user_id>/<int:index>/', views.scoring),
	#心得
	path('memo/<int:classroom_id>/', views.memo),
    path('check/<int:typing>/<int:unit>/<int:user_id>/<int:classroom_id>/', views.check),
	#成績
	path('grade/<int:typing>/<int:unit>/<int:classroom_id>/', views.grade),
	path('grade/excel/<int:typing>/<int:unit>/<int:classroom_id>/', views.grade_excel), 	
# 思辨區
    path('speculation/<int:categroy>/<int:categroy_id>/', login_required(views.SpeculationAllListView.as_view()), name='forum-all'),  
    path('speculation/show/<int:forum_id>/', login_required(views.speculation_show), name='forum-show'),    
    path('speculation/edit/<int:classroom_id>/<int:pk>/', login_required(views.SpeculationEditUpdateView.as_view()), name='forum-edit'),   
    path('speculation/<int:classroom_id>/', login_required(views.SpeculationListView.as_view()), name='forum-list'),
    path('speculation/add/<int:classroom_id>/', login_required(views.SpeculationCreateView.as_view()), name='forum-add'),
    path('speculation/category/<int:classroom_id>/<int:forum_id>/', login_required(views.speculation_categroy), name='forum-category'),  
    path('speculation/deadline/<int:classroom_id>/<int:forum_id>/', login_required(views.speculation_deadline), name='forum-deadline'),  
    path('speculation/deadline/set/', login_required(views.speculation_deadline_set), name='forum-deatline-set'), 
    path('speculation/deadline/date/', login_required(views.speculation_deadline_date), name='forum-deatline-date'),   
    path('speculation/deadline/<int:classroom_id>/<int:forum_id>/', login_required(views.speculation_deadline), name='forum-category'),   
    path('speculation/download/<int:content_id>/', views.speculation_download, name='forum-download'),  
    path('speculation/content/<int:forum_id>/', login_required(views.SpeculationContentListView.as_view()), name='forum-content'), 
    path('speculation/content/add/<int:forum_id>/', login_required(views.SpeculationContentCreateView.as_view()), name='forum-content-add'),
    path('speculation/content/delete/<int:forum_id>/<int:content_id>/', login_required(views.speculation_delete), name='forum-content-delete'),   
    path('speculation/content/edit/<int:forum_id>/<int:content_id>/', login_required(views.speculation_edit), name='forum-content-edit'),    
    #path('forum/class/<int:classroom_id>/<int:forum_id>/', views.forum_class, name='forum-class'),  
    path('speculation/class/<int:forum_id>/',  login_required(views.SpeculationClassListView.as_view()), name='forum-class'),    
    path('speculation/export/<int:classroom_id>/<int:forum_id>/', login_required(views.speculation_export), name='forum-export'),   
    path('speculation/grade/<int:classroom_id>/<int:action>/', login_required(views.speculation_grade)),   
    #設定班級
    path('speculation/class/switch/', login_required(views.speculation_switch), name='make'),
    #設定分組
    path('speculation/group/<int:classroom_id>/<int:forum_id>/', login_required(views.speculation_group), name='group'),  
    path('speculation/group/set/', login_required(views.speculation_group_set), name='group'),   
    #文字註記
    path('speculation/annotation/<int:forum_id>/', login_required(views.SpeculationAnnotationListView.as_view()), name='make'),   
    path('speculation/annotation/add/<int:forum_id>/', login_required(views.SpeculationAnnotationCreateView.as_view()), name='forum-content-add'),
    path('speculation/annotation/delete/<int:forum_id>/<int:content_id>/', login_required(views.speculation_annotation_delete), name='forum-content-delete'),   
    path('speculation/annotation/edit/<int:forum_id>/<int:content_id>/', login_required(views.speculation_annotation_edit), name='forum-content-edit'),    
    #  測驗區
    path('exam/<int:categroy>/<int:categroy_id>/', login_required(views.ExamAllListView.as_view())),  
    path('exam/<int:classroom_id>/', login_required(views.ExamListView.as_view())),
    path('exam/add/<int:classroom_id>/', login_required(views.ExamCreateView.as_view())),
    path('exam/edit/<int:classroom_id>/<int:pk>/', login_required(views.ExamEditUpdateView.as_view())),   
    path('exam/category/<int:classroom_id>/<int:exam_id>/', login_required(views.exam_categroy)),  
    path('exam/class/<int:exam_id>/',  login_required(views.ExamClassListView.as_view())), 
    path('exam/class/switch/', login_required(views.exam_switch)),        
    path('exam/deadline/<int:classroom_id>/<int:exam_id>/', login_required(views.exam_deadline)),  
    path('exam/deadline/set/', login_required(views.exam_deadline_set)), 
	path('exam/deadline/date/', login_required(views.exam_deadline_date)),   
    path('exam/round/<int:classroom_id>/<int:exam_id>/', login_required(views.exam_round)),   	
    path('exam/round/set/', login_required(views.exam_round_set)), 	
    path('exam/question/<int:exam_id>/', login_required(views.ExamQuestionListView.as_view())), 
    path('exam/question/add/<int:exam_id>/', login_required(views.ExamQuestionCreateView.as_view())),
    path('exam/question/delete/<int:exam_id>/<int:question_id>/', login_required(views.exam_question_delete)),   
    path('exam/question/edit/<int:exam_id>/<int:question_id>/', login_required(views.exam_question_edit)), 
    path('exam/publish/<int:exam_id>/', login_required(views.exam_publish)),        
    path('exam/check/<int:exam_id>/<int:question_id>/', login_required(views.exam_check)),  
    path('exam/check/make/', login_required(views.exam_check_make)),        
    path('exam/score/<int:classroom_id>/<int:exam_id>/', login_required(views.exam_score)), 
    path('exam/excel/<int:classroom_id>/<int:exam_id>/', login_required(views.exam_excel)),      	
	#大量匯入選擇題
    path('exam/import/upload/<int:types>/<int:exam_id>/', login_required(views.exam_import_sheet)),   	
    path('exam/import/question/<int:types>/<int:exam_id>/', login_required(views.exam_import_question)),   
    # 合作區
    #path('team/<int:categroy>/<int:categroy_id>/', login_required(TeamAllListView.as_view())),  
    #path('forum/show/<int:forum_id>/', login_required(views.forum_show), name='forum-show'),    
    path('team/edit/<int:classroom_id>/<int:pk>/', login_required(views.TeamEditUpdateView.as_view())),   
    path('team/<int:classroom_id>/', login_required(views.TeamListView.as_view())),
    path('team/add/<int:classroom_id>/', login_required(views.TeamCreateView.as_view())),
    path('team/category/<int:classroom_id>/<int:team_id>/', login_required(views.team_categroy)),  
    path('team/deadline/<int:classroom_id>/<int:team_id>/', login_required(views.team_deadline)),  
    path('team/deadline/set/', login_required(views.team_deadline_set)), 
    path('team/deadline/date/', login_required(views.team_deadline_date)),   
    path('team/deadline/<int:classroom_id>/<int:team_id>/', login_required(views.team_deadline)),   
    #path('forum/download/<int:content_id>/', views.forum_download, name='forum-download'),  
    #path('forum/content/<int:forum_id>/', login_required(ForumContentListView.as_view()), name='forum-content'), 
    #path('forum/content/add/<int:forum_id>/', login_required(ForumContentCreateView.as_view()), name='forum-content-add'),
    #path('forum/content/delete/<int:forum_id>/<int:content_id>/', login_required(views.forum_delete), name='forum-content-delete'),   
    #path('forum/content/edit/<int:forum_id>/<int:content_id>/', login_required(views.forum_edit), name='forum-content-edit'),    
    path('team/class/<int:classroom_id>/<int:team_id>/', views.team_class),  
    path('team/class/<int:team_id>/',login_required(views.TeamClassListView.as_view())),  	
    path('team/class/switch/', login_required(views.team_switch)),      	
    path('team/group/<int:classroom_id>/<int:team_id>/', login_required(views.team_group)),
    path('team/group/set/', login_required(views.team_group_set)),	
	# 影片觀看記錄
    path('video/<int:classroom_id>/<int:forum_id>/<int:work_id>/', views.EventVideoView.as_view()),
    path('video/length/', views.video_length),	
	path('video/user/<int:classroom_id>/<int:content_id>/<int:user_id>/', views.VideoListView.as_view()), 	
]