# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta

# 班級
class Classroom(models.Model):
    Lesson_CHOICES = [		
        (0, '數位學習：SPOC線上課程'),	         
        (1, '程式設計輕鬆學：使用Scratch3.X'),                          
        (2, '※基礎程式設計：使用Scratch3.X'),                
		]	
		
    Progress_CHOICES = [				
        (0, '個人'),  
        (1, '小組'),  
		]	

    Online_CHOICES = [				
        (False, '關閉課程'),  
        (True, '開放修課'),    		
		]	

    LessonShort_CHOICES = [	
        (0, 'SPOC'),
        (1, 'Scratch-6'),             
        (2, 'Scratch-7'),                                     
		]		
		
    # 班級名稱
    name = models.CharField(max_length=30, verbose_name='班級名稱')
    # 課程名稱
    lesson = models.IntegerField(default=2, choices=Lesson_CHOICES, verbose_name='課程名稱')			
    # 選課密碼
    password = models.CharField(max_length=30, verbose_name='選課密碼')
    # 授課教師
    teacher_id = models.IntegerField(default=0)
    # 使用分組
    group = models.IntegerField(default=0)
    # 是否開放創意秀分組
    group_show_open = models.BooleanField(default=False)
    # 組別人數
    group_show_size = models.IntegerField(default=2)  
    # 學生進度
    progress = models.IntegerField(default=1, choices=Progress_CHOICES, verbose_name='學生進度')  
    # 學生進度
    online = models.BooleanField(default=True, choices=Online_CHOICES, verbose_name='課程狀態') 

    @property
    def teacher(self):
        return User.objects.get(id=self.teacher_id)  
        
    def __unicode__(self):
        return self.name
        
    def lesson_choice(self):
        return dict(Classroom.LessonShort_CHOICES)[self.lesson] 
		
#匯入
class ImportUser(models.Model):
	username = models.CharField(max_length=50, default="")
	password = models.CharField(max_length=50, default="")
	email = models.CharField(max_length=100, default="")

#班級助教
class Assistant(models.Model):
    classroom_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)	
	
#討論區
class FWork(models.Model):
    title = models.CharField(max_length=250,verbose_name= '討論主題')
    teacher_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)

def get_deadline():
    return datetime.today() + timedelta(days=14)

class FClass(models.Model):
    forum_id = models.IntegerField(default=0)
    classroom_id =  models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=timezone.now)
    deadline = models.BooleanField(default=False)
    deadline_date = models.DateTimeField(default=get_deadline)

    def __unicode__(self):
        return str(self.forum_id)

class FContent(models.Model):
    forum_id =  models.IntegerField(default=0)
    types = models.IntegerField(default=0)
    title = models.CharField(max_length=250,null=True,blank=True)
    memo = models.TextField(default='')
    link = models.CharField(max_length=250,null=True,blank=True)
    youtube = models.CharField(max_length=250,null=True,blank=True)
    youtube_length = models.IntegerField(default=0)
    file = models.FileField(blank=True,null=True)
    filename = models.CharField(max_length=60,null=True,blank=True)	
	
#自訂作業
class TWork(models.Model):
    title = models.CharField(max_length=250)	
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
	

#思辨區
class SpeculationWork(models.Model):
    title = models.CharField(max_length=250,verbose_name= '思辨主題')
    teacher_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
    domains = models.TextField(default='')
    levels = models.TextField(default='')

class SpeculationClass(models.Model):
    forum_id = models.IntegerField(default=0)
    classroom_id =  models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=timezone.now)
    deadline = models.BooleanField(default=False)
    deadline_date = models.DateTimeField(default=get_deadline)
    group =  models.IntegerField(default=0)

    def __unicode__(self):
        return str(self.forum_id)

class SpeculationContent(models.Model):
    forum_id =  models.IntegerField(default=0)
    types = models.IntegerField(default=0)
    title = models.CharField(max_length=250,null=True,blank=True)
    memo = models.TextField(default='')
    text = models.TextField(default='')
    link = models.CharField(max_length=250,null=True,blank=True)
    youtube = models.CharField(max_length=250,null=True,blank=True)
    file = models.FileField(blank=True,null=True)
    filename = models.CharField(max_length=60,null=True,blank=True)

class SpeculationAnnotation(models.Model):
    forum_id =  models.IntegerField(default=0)
    kind = models.CharField(max_length=250,null=True,blank=True)
    color = models.CharField(max_length=7,null=True,blank=True)

class ClassroomGroup(models.Model):
    # 班級
    classroom_id = models.IntegerField(default=0)
    #分組名稱
    title = models.CharField(max_length=250,null=True,blank=True)
    #小組數目
    numbers = models.IntegerField(default=6)
    #開放分組
    opening = models.BooleanField(default=True)
    #分組方式
    assign = models.IntegerField(default=0)

    def __unicode__(self):
        return self.classroom_id

#測驗
class Exam(models.Model):
    title = models.CharField(max_length=250,verbose_name= '測驗主題')
    user_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
    domains = models.TextField(default='')
    levels = models.TextField(default='')
    opening = models.BooleanField(default=False)


class ExamClass(models.Model):
    exam_id = models.IntegerField(default=0)
    classroom_id =  models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=timezone.now)
    deadline = models.BooleanField(default=False)
    deadline_date = models.DateTimeField(default=get_deadline)
    round_limit = models.IntegerField(default=1)

    def __unicode__(self):
        return str(self.exam_id)

    class Meta:
        unique_together = ('exam_id', 'classroom_id',)

class ExamQuestion(models.Model):
    exam_id = models.IntegerField(default=0)
    types = models.IntegerField(default=0)
    #題目敘述
    title = models.TextField(default='')
    title_pic = models.FileField(blank=True,null=True)
    title_filename = models.CharField(max_length=60,null=True,blank=True)    
    #選擇題選項
    option1 = models.CharField(max_length=250,null=True,blank=True)
    option2 = models.CharField(max_length=250,null=True,blank=True)
    option3 = models.CharField(max_length=250,null=True,blank=True)
    option4 = models.CharField(max_length=250,null=True,blank=True) 
    #簡答題
    answer = models.TextField(default='')
    #配分 
    score = models.IntegerField(default=0)

class ExamImportQuestion(models.Model):
    title = models.TextField(default='')
    option1 = models.CharField(max_length=250,null=True,blank=True)
    option2 = models.CharField(max_length=250,null=True,blank=True)
    option3 = models.CharField(max_length=250,null=True,blank=True)
    option4 = models.CharField(max_length=250,null=True,blank=True)
    answer= models.TextField(default='')
    score = models.IntegerField(default=0)    

#合作區
class TeamWork(models.Model):
    title = models.CharField(max_length=250,verbose_name= '任務主題')
    teacher_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    time = models.DateTimeField(default=timezone.now)
    domains = models.TextField(default='')
    levels = models.TextField(default='')

class TeamClass(models.Model):
    team_id = models.IntegerField(default=0)
    classroom_id =  models.IntegerField(default=0)
    group =  models.IntegerField(default=0)
    publication_date = models.DateTimeField(default=timezone.now)
    deadline = models.BooleanField(default=False)
    deadline_date = models.DateTimeField(default=get_deadline)

    def __unicode__(self):
        return str(self.team_id)

    class Meta:
        unique_together = ('team_id', 'classroom_id',)

class TeamContent(models.Model):
    team_id =  models.IntegerField(default=0)
    types = models.IntegerField(default=0)
    title = models.CharField(max_length=250,null=True,blank=True)
    memo = models.TextField(default='')
    link = models.CharField(max_length=250,null=True,blank=True)
    youtube = models.CharField(max_length=250,null=True,blank=True)
    file = models.FileField(blank=True,null=True)
    filename = models.CharField(max_length=60,null=True,blank=True)