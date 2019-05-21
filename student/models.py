# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User
from teacher.models import Classroom
from django.utils import timezone
from django.core.validators import RegexValidator, validate_comma_separated_integer_list

# 學生選課資料
class Enroll(models.Model):
    # 學生序號
    student_id = models.IntegerField(default=0)
    # 班級序號
    classroom_id = models.IntegerField(default=0)
    # 座號
    seat = models.IntegerField("座號", default=0)
    # 電腦
    computer = models.IntegerField("電腦", default=0)   
    # 組別
    group = models.IntegerField(default=-1)
    # 創意秀組別
    #groupshow = models.CommaSeparatedIntegerField(max_length=200)
    groupshow = models.CharField(validators=[validate_comma_separated_integer_list], max_length=200) 
    # 心得
    score_memo0 = models.IntegerField(default=0)    
    score_memo1 = models.IntegerField(default=0)
    score_memo2 = models.IntegerField(default=0)    
    score_memo0_custom = models.IntegerField(default=0)	
    score_memo1_custom = models.IntegerField(default=0)	
    score_memo2_custom = models.IntegerField(default=0)	        
    
    @property
    def classroom(self):
        return Classroom.objects.get(id=self.classroom_id)

    @property
    def student(self):
        return User.objects.get(id=self.student_id)      

    def __str__(self):
        return str(self.id) + ":" + str(self.classroom_id) + ":" + str(self.student_id)
        
    def set_foo(self, x):
        self.groupshow = json.dumps(x)

    def get_groupshow(self):
        return json.loads(self.groupshow)     

    class Meta:
        unique_together = ('classroom_id', 'student_id')	

		
# 小老師
class WorkAssistant(models.Model):
    student_id = models.IntegerField(default=0)
    typing = models.IntegerField(default=0)
    group = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    lesson = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)    

    @property
    def student(self):
        return User.objects.get(id=self.student_id)

class WorkGroup(models.Model):
    typing = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    group_id = models.IntegerField(default=0)

    class Meta:
        unique_together = ('classroom_id', 'index', 'typing')	


class Work(models.Model):
    user_id = models.IntegerField(default=0)
    lesson = models.IntegerField(default=0)
    typing = models.IntegerField(default=0)
    index = models.IntegerField()
    memo = models.TextField()
    publication_date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=-1)
    scorer = models.IntegerField(default=0)
    # scratch
    file = models.FileField()
    comment = models.TextField()	

    def __unicode__(self):
        user = User.objects.filter(id=self.user_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

    @property
    def user(self):
        return User.objects.get(id=self.user_id)

class WorkFile(models.Model):
    work_id = models.IntegerField(default=0)
    filename = models.TextField()
    upload_date = models.DateTimeField(default=timezone.now)		
	
#討論區作業
class SFWork(models.Model):
    student_id = models.IntegerField(default=0)
    index = models.IntegerField(default=0)
    memo = models.TextField(default='')
    memo_e =  models.IntegerField(default=0)
    memo_c = models.IntegerField(default=0)		
    publish = models.BooleanField(default=False)
    publication_date = models.DateTimeField(default=timezone.now)
    reply_date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)
    scorer = models.IntegerField(default=0)
    comment = models.TextField(default='',null=True,blank=True)
    comment_publication_date = models.DateTimeField(default=timezone.now)		
    likes = models.TextField(default='')
    like_count = models.IntegerField(default=0)	
    reply = models.IntegerField(default=0)
		
    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

class SFContent(models.Model):
    index =  models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
    work_id = models.IntegerField(default=0)
    title =  models.CharField(max_length=250,null=True,blank=True)
    filename = models.CharField(max_length=60,null=True,blank=True)    
    publication_date = models.DateTimeField(default=timezone.now)
    delete_date = models.DateTimeField(default=timezone.now)		
    visible = models.BooleanField(default=True)

#討論留言
class SFReply(models.Model):
    index = models.IntegerField(default=0)
    work_id =  models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    memo =  models.TextField(default='')
    publication_date = models.DateTimeField(default=timezone.now)        
	
	

class StudentGroup(models.Model):
    group_id = models.IntegerField(default=0)
    enroll_id = models.IntegerField(default=0)
    group = models.IntegerField(default=0)		

    class Meta:
        unique_together = ('enroll_id', 'group_id',)		

class StudentGroupLeader(models.Model):
    group_id = models.IntegerField(default=0)
    group = models.IntegerField(default=0)	
    enroll_id = models.IntegerField(default=0)	

    class Meta:
        unique_together = ('group_id', 'group')		


#思辨文章
class SSpeculationWork(models.Model):
    student_id = models.IntegerField(default=0)
    index = models.IntegerField()
    memo = models.TextField(default='')
    publish = models.BooleanField(default=False)
    publication_date = models.DateTimeField(default=timezone.now)
    reply_date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)
    scorer = models.IntegerField(default=0)
    comment = models.TextField(default='',null=True,blank=True)
    comment_publication_date = models.DateTimeField(default=timezone.now)	
    likes = models.TextField(default='')
    like_count = models.IntegerField(default=0)	
    reply = models.IntegerField(default=0)
		
    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"

class SSpeculationContent(models.Model):
    index =  models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
    work_id = models.IntegerField(default=0)
    title =  models.CharField(max_length=250,null=True,blank=True)
    filename = models.CharField(max_length=60,null=True,blank=True)    
    publication_date = models.DateTimeField(default=timezone.now)
    delete_date = models.DateTimeField(default=timezone.now)		
    visible = models.BooleanField(default=True)
	        		

#測驗
class ExamWork(models.Model):
    student_id = models.IntegerField(default=0)
    exam_id = models.IntegerField()    
    questions = models.TextField(default='')
    publish = models.BooleanField(default=False)
    publication_date = models.DateTimeField(default=timezone.now)
    score = models.IntegerField(default=0)
    scorer = models.IntegerField(default=0)
		
    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        exam_id = self.exam_id
        return user.first_name+"("+str(exam_id)+")"		
			
#測驗答案
class ExamAnswer(models.Model):
    examwork_id = models.IntegerField(default=0)
    question_id = models.IntegerField(default=0)
    student_id = models.IntegerField(default=0)
    answer = models.TextField(default='')
    answer_right = models.BooleanField(default=False)
		
    class Meta:
        unique_together = ('student_id', 'examwork_id', 'question_id')		
		
class TeamContent(models.Model):
    team_id =  models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)  
    types = models.IntegerField(default=0)
    title = models.CharField(max_length=250,null=True,blank=True)
    memo = models.TextField(default='')
    link = models.CharField(max_length=250,null=True,blank=True)
    youtube = models.CharField(max_length=250,null=True,blank=True)
    youtube_length = models.IntegerField(default=0)
    file = models.FileField(blank=True,null=True)
    filename = models.CharField(max_length=60,null=True,blank=True)
    publication_date = models.DateTimeField(default=timezone.now)    
    publish = models.BooleanField(default=False)

class CourseContentProgress(models.Model):
    student_id = models.IntegerField(default=0)  
    content_id = models.IntegerField(default=0)  
    progress =models.IntegerField(default=0)  
    start_time = models.DateTimeField(default=timezone.now)    
    finish_time = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('student_id', 'content_id')		    
      
# 測驗
class ScratchExam(models.Model):
    exam_id = models.IntegerField()
    student_id = models.IntegerField()
    answer = models.TextField()
    score = models.IntegerField()
    test_time = models.DateTimeField(default=timezone.now)

#解答
class ScratchAnswer(models.Model):
    student_id = models.IntegerField(default=0)
    lesson_id = models.IntegerField(default=0)
    index = models.IntegerField()

    def __unicode__(self):
        user = User.objects.filter(id=self.student_id)[0]
        index = self.index
        return user.first_name+"("+str(index)+")"
