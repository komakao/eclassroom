from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('lessons/<int:subject_id>/', views.lessons),
    path('lesson/<int:lesson>/<int:unit>/<int:index>/', views.lesson),  
    path('lessons1/<slug:subject_id>/', views.lessons1),
    path('lesson1/<slug:lesson>/', views.lesson1),   
    path('classroom/', views.ClassroomList.as_view()),
    path('classroom/join/<int:kind>', views.ClassroomJoinList.as_view()),    
    path('classroom/<int:pk>/enroll/', views.ClassroomEnrollCreate.as_view()), 
    path('classroom/<int:pk>/classmate/', views.ClassmateList.as_view()),    
    path('classroom/<int:pk>/seat/', views.ClassroomSeatUpdate.as_view()),  
    path('classroom/<int:pk>/computer/', views.ClassroomComputerUpdate.as_view()),       
    #組別
    #path('group/<int:classroom_id>/', views.GroupPanel.as_view()),
    #path('group/join/<int:classroom_id>/<int:number>/<int:enroll_id>/', views.GroupJoin.as_view()),
    #組別
    path('group/<int:classroom_id>/', views.GroupListView.as_view()),
    path('group/list/<int:group_id>/', views.group_list),
    path('group/add/<int:group_id>/<int:number>/<int:enroll_id>/', views.group_join),	
    path('group/leader/<int:group_id>/<int:number>/<int:enroll_id>/', views.group_leader),	 	
    #查詢該作業分組小老師
    path('group/work/<int:typing>/<int:lesson>/<int:index>/<int:classroom_id>/', views.work_group),  	
    #公告
    path('announce/<int:classroom_id>/', views.AnnounceListView.as_view()),  	
    #作業上傳
    path('work/<int:typing>/<int:classroom_id>/', views.work),  
    path('work/download/<int:typing>/<int:lesson>/<int:index>/<int:user_id>/<int:workfile_id>/', views.work_download),  	
    path('work/groups/<int:classroom_id>/', views.work_groups),	
    path('work/show/<int:typing>/<int:lesson>/<int:index>/<int:user_id>/', views.show),
    path('work/submit/<int:typing>/<int:lesson>/<int:index>/', views.submit),	
    # 作業進度查詢
    path('progress/<int:typing>/<int:classroom_id>/<int:group_id>/', views.progress),  	
    #查詢該作業所有同學心得
    path('memo/<int:typing>/<int:classroom_id>/<int:index>/', views.memo),   
    path('memo/user/<int:typing>/<int:user_id>/<int:lesson>/<int:classroom_id>', views.memo_user),	
    #查詢某班級所有同學心得		
    path('memo/show/<int:typing><int:user_id>/<int:unit>/<int:classroom_id>/<int:score>/', views.memo_show),	
    path('memo/count/<int:typing>/<int:classroom_id>/<int:index>/', views.memo_count),        	
    path('memo/word/<int:typing>/<int:classroom_id>/<int:index>/<str:word>/', views.memo_word),
    #討論區
    path('forum/<int:classroom_id>/<int:bookmark>/', views.ForumList.as_view()),  
    path('forum/show/<int:index>/<int:user_id>/<int:classroom_id>/', views.ForumShow.as_view()),   
    path('forum/submit/<int:classroom_id>/<int:index>/', views.ForumSubmit.as_view()),    
	path('forum/publish/<int:classroom_id>/<int:index>/', views.ForumPublish.as_view()),
  	path('forum/publish/done/<int:classroom_id>/<int:index>/', views.ForumPublishDone.as_view()),
    path('forum/memo/<int:classroom_id>/<int:index>/<int:action>/', views.ForumMemo.as_view()),  
    #path('forum/file_delete/', login_required(views.forum_file_delete)), 	
    path('forum/history/<int:user_id>/<int:index>/<int:classroom_id>/', views.ForumHistory.as_view()),  
    path('forum/like/', views.forum_like),    
    path('forum/reply/', views.forum_reply),    	
    path('forum/people/', views.forum_people), 
    path('forum/guestbook/', views.forum_guestbook), 	
    path('forum/score/', views.forum_score),   
    path('forum/jieba/<int:classroom_id>/<int:index>/', views.ForumJieba.as_view()), 	
    path('forum/word/<int:classroom_id>/<int:index>/<str:word>/', views.ForumWord.as_view()),  
	path('forum/download/<int:file_id>/', views.forum_download), 
    path('forum/showpic/<int:file_id>/', views.forum_showpic), 		
	#問卷區
	path('survey/<int:classroom_id>', views.survey),	
    #思辨
    path('speculation/<int:classroom_id>/<int:bookmark>/', login_required(views.SpeculationListView.as_view()), name='work-list'),  
    path('speculation/submit/<int:classroom_id>/<int:index>/', login_required(views.speculation_submit)),    
	path('speculation/publish/<int:classroom_id>/<int:index>/<int:action>/', login_required(views.speculation_publish), name='speculation-publish'), 	
	path('speculation/annotate/<int:classroom_id>/<int:index>/<int:id>/', login_required(views.SpeculationAnnotateView.as_view()), name='speculation-annotate'), 	
	path('speculation/annotateclass/<int:classroom_id>/<int:index>/<int:id>/', login_required(views.SpeculationAnnotateClassView.as_view()), name='speculation-annotate-class'), 		
	path('speculation/download/<int:file_id>/', views.speculation_download, name='forum-download'), 
	path('speculation/showpic/<int:file_id>/', login_required(views.speculation_showpic), name='forum-showpic'), 		
    path('speculation/score/', login_required(views.speculation_score)), 
	#測驗
	path('exam/<int:classroom_id>/', login_required(views.ExamListView.as_view())), 
	path('exam/question/<int:classroom_id>/<int:exam_id>/<int:examwork_id>/<int:question_id>/', login_required(views.exam_question)), 	
	path('exam/answer/', login_required(views.exam_answer)), 	
	path('exam/submit/<int:classroom_id>/<int:exam_id>/<int:examwork_id>/', login_required(views.exam_submit)), 
	path('exam/score/<int:classroom_id>/<int:exam_id>/<int:examwork_id>/<int:user_id>/<int:question_id>/', login_required(views.exam_score)), 
    path('video/log/', views.video_log),
	#合作
	path('team/<int:classroom_id>/', login_required(views.TeamListView.as_view())), 
	path('team/stage/<int:classroom_id>/<int:grouping>/<int:team_id>/', login_required(views.team_stage)),                 
    path('team/content/<int:classroom_id>/<int:grouping>/<int:team_id>/<int:publish>/<int:stage>', login_required(views.TeamContentListView.as_view())), 
    path('team/content/add/<int:classroom_id>/<int:grouping>/<int:team_id>/', login_required(views.TeamContentCreateView.as_view())),
    path('team/content/delete/<int:classroom_id>/<int:grouping>/<int:team_id>/<int:content_id>/', login_required(views.team_delete)),   
    path('team/content/edit/<int:classroom_id>/<int:grouping>/<int:team_id>/<int:content_id>/', login_required(views.team_edit)),    
    path('team/publish/', login_required(views.team_make_publish)),             
    #測驗
    path('exam/', views.exam),
    path('exam_check/', views.exam_check),
    path('exam/score/', views.exam_score),    
]