from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

# 大廳訊息	
class Message(models.Model):
    author_id = models.IntegerField(default=0)
    reader_id = models.IntegerField(default=0)
    type = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    title = models.CharField(max_length=250)
    content = models.TextField(default='')
    url = models.CharField(max_length=250)
    time = models.DateTimeField(auto_now_add=True)

    #def __str__(self):
    #    return self.title
		
    @classmethod
    def create(cls, title, url, time):
        message = cls(title=title, url=url, time=time)
        return message
      
# 訊息    
class MessagePoll(models.Model):
    message_type = models.IntegerField(default=0)  
    message_id = models.IntegerField(default=0)
    reader_id = models.IntegerField(default=0)
    classroom_id = models.IntegerField(default=0)
    read = models.BooleanField(default=False)
    
    @property
    def message(self):
        return Message.objects.get(id=self.message_id)        

class MessageFile(models.Model):
    message_id = models.IntegerField(default=0) 
    filename = models.TextField()
    before_name = models.TextField()
    upload_date = models.DateTimeField(default=timezone.now)

class MessageContent(models.Model):
    message_id =  models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    title =  models.CharField(max_length=250,null=True,blank=True)
    filename = models.CharField(max_length=250,null=True,blank=True)    
    publication_date = models.DateTimeField(default=timezone.now)
	
# 個人檔案資料
class Profile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
	# 1積分：上傳作業
  work = models.IntegerField(default=0)
	# 2積分：擔任小老師
  assistant = models.IntegerField(default=0)
	# 3積分：創意秀
  creative = models.IntegerField(default=0)	
    # 4積分：討論區
  forum = models.IntegerField(default=0)
	# 5積分：按讚
  like = models.FloatField(default=0.0)
	# 6積分：留言
  reply = models.FloatField(default=0.0)
	# 大頭貼等級
  avatar = models.IntegerField(default=0)
	# 訪客人次
  home_count = models.IntegerField(default=0)
  visitor_count = models.IntegerField(default=0)
	# 開站時間
  open_time = models.DateTimeField(auto_now_add=True)
  # 選課班級
  classroom = models.TextField()
	# Scrattch
  lock1 = models.IntegerField(default=0)  
      
# 積分記錄 
class PointHistory(models.Model):
    # 使用者序號
	user_id = models.IntegerField(default=0)
	# 積分類別 1:上傳作業 2:小老師
	kind = models.IntegerField(default=0)
	# 積分項目
	message = models.CharField(max_length=100)	
	# 將積分項目超連結到某個頁面
	url = models.CharField(max_length=100)
	# 記載時間 
	publish = models.DateTimeField(default=timezone.now)

	def __unicode__(self):
		return str(self.user_id)
	  
# 訪客 
class Visitor(models.Model):
    date = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    
# 訪客記錄
class VisitorLog(models.Model):
    visitor_id = models.IntegerField(default=0)    
    user_id = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now_add=True)		    
    
    @property        
    def user(self):
        return User.objects.get(id=self.user_id)       
		
#日期計數器
class DayCounter(models.Model):
	day = models.CharField(max_length=8)
	hit = models.IntegerField(default=0)	
	
#計數器記錄
class LogCounter(models.Model):
	counter_id = models.IntegerField(default=0)
	counter_date = models.DateTimeField(default=timezone.now)
	counter_ip = models.CharField(max_length=20)
  
#課程計數器
class LessonCounter(models.Model):
	name = models.CharField(max_length=10)
	hit = models.IntegerField(default=0)

# 學習領域
class Domain(models.Model):
	title = models.CharField(max_length=200, default="",verbose_name= '領域名稱')
	
# 年級
class Level(models.Model):
  title = models.CharField(max_length=200, default="",verbose_name= '年級')

