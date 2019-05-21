from django import template
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from teacher.models import *
from student.models import *
from account.models import *
from survey.models import *
from student.lesson import *
import json
import re

register = template.Library()

@register.filter(takes_context=True)
def nickname(user_id):
    try: 
        user = User.objects.get(id=user_id)
        return user.first_name
    except :
        pass
    return ""
	
@register.filter(name='has_group') 
def has_group(user, group_name):
    try:
        group =  Group.objects.get(name=group_name) 
    except ObjectDoesNotExist:
        group = None
    return group in user.groups.all()
	
@register.filter
def teacher_classroom(user_id, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if classroom.teacher_id == user_id:
        return True
    else:
        assistants = Assistant.objects.filter(classroom_id=classroom_id, user_id=user_id)
        if len(assistants) > 0 :
            return True
    return False
		
@register.filter
def seat(user_id, classroom_id):
    try:
        enroll = Enroll.objects.get(student_id=user_id, classroom_id=classroom_id)
    except ObjectDoesNotExist:
        return 0
    except MultipleObjectsReturned:
        return enroll[0].seat
    return enroll.seat	
	
@register.filter
def enroll(user_id, classroom_id):
    try:
        enroll = Enroll.objects.get(student_id=user_id, classroom_id=classroom_id)
    except ObjectDoesNotExist:
        return 0
    except MultipleObjectsReturned:
        return enroll[0].id
    return enroll.id
@register.filter(takes_context=True)
def read_already(message_id, user_id):
    try:
        messagepoll = MessagePoll.objects.get(message_id=message_id, reader_id=user_id)
    except ObjectDoesNotExist:
        messagepoll = MessagePoll()
    return messagepoll.read    
	
@register.filter(name="img")
def img(title):
    if title.startswith(u'[私訊]'):
        return "line"
    elif title.startswith(u'[公告]'):
        return "announce"
    elif u'擔任小老師' in title:
        return "assistant"
    elif u'設您為教師' in title:
        return "teacher"
    else :
        return ""
		
@register.filter
def student_username(name):
    start = "_"
    student = name[name.find(start)+1:]
    return student
	
@register.filter
def teacher_group(user):
    return user.groups.filter(name='teacher').exists()
	
@register.filter(name='assistant') 
def assistant(user_id):
    assistants = Assistant.objects.filter(user_id=user_id)
    if assistants:
      return True
    return False
	
@register.filter
def pre_survey_done(user_id):
    surveys = PreSurvey.objects.filter(student_id=user_id)
    if len(surveys)>0:
        return True
    else:
        return False
			
@register.filter
def post_survey_done(user_id):
    surveys = PostSurvey.objects.filter(student_id=user_id)
    if len(surveys)>0:
        return True
    else:
        return False		
		
@register.filter
def lesson_name(lesson, index):
        lesson_dict = {}
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2]
        else:
            for unit1 in lesson_list[int(lesson)-2][1]:
                for assignment in unit1[1]:
                    lesson_dict[assignment[2]] = assignment[0]
        return lesson_dict[int(index)]

@register.filter
def group_name(group_id):
    if group_id > 0 :
        title = ClassroomGroup.objects.get(id=group_id).title
        return title 
    else :
        return ""    
	
@register.filter
def twork_title(index):
    try:
        twork = TWork.objects.get(id=index)
        return twork.title
    except ObjectDoesNotExist:
        return ""

@register.filter
def twork_time(index):
    try:
        twork = TWork.objects.get(id=index)
        return twork.time
    except ObjectDoesNotExist:
        return ""

@register.filter
def unit_name(unit, lesson):
    if lesson == 1:
        return lesson_list1[2]
    return lesson_list[int(lesson)-2][1][int(unit)-1][0]
	
@register.filter
def lesson_download(lesson, index):
        lesson_dict = {}
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2]
        else:
            for unit1 in lesson_list[int(lesson)-2][1]:
                for assignment in unit1[1]:
                    lesson_dict[assignment[2]] = assignment[1]
        return lesson_dict[int(index)]
			
@register.filter
def lesson_resource1(lesson, index):
        lesson_dict = {}
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2]
        else:
            for unit1 in lesson_list[int(lesson)-2][1]:
                for assignment in unit1[1]:
                    lesson_dict[assignment[2]] = assignment[4]
            if lesson_dict[int(index)] :
                return lesson_dict[int(index)][0]
            else :
                return False
			
@register.filter
def lesson_resource2(lesson, index):
        lesson_dict = {}
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2] 
        else:                  
            for unit1 in lesson_list[int(lesson)-2][1]:
                for assignment in unit1[1]:
                    lesson_dict[assignment[2]] = assignment[4]
            if lesson_dict[int(index)] :
                return lesson_dict[int(index)][1]
            else :
                return False
			
@register.filter
def lesson_youtube(lesson, index):
        lesson_dict = {}
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[5] 
            if lesson_dict[index] :
                return lesson_dict[index]
            else :
                return False                
        else:       
            for unit1 in lesson_list[int(lesson)-2][1]:
                for assignment in unit1[1]:
                    lesson_dict[assignment[2]] = assignment[5]
            if lesson_dict[index] :
                return lesson_dict[index]
            else :
                return False

@register.filter
def subtract(a, b):
    return a - b			
	
@register.filter
def classname(classroom_id):
    try: 
        classroom = Classroom.objects.get(id=classroom_id)
        return classroom.name
    except ObjectDoesNotExist:
        pass
        return ""  	
		
@register.filter()
def memo(text):
  memo = re.sub(r"\n", r"<br/>", re.sub(r"\[m_(\d+)#(\d\d:\d\d:\d\d)\]", r"<button class='btn btn-default btn-xs btn-marker' data-mid='\1' data-time='\2'><span class='badge'>\1</span> \2</button>",text))
  return memo		
  
@register.filter
def number(url):
    number_pos = url.find("v=")
    if number_pos > 0:
        number = url[number_pos+2:number_pos+13]
    else :
        number_pos = url.find("youtu.be/")
        number = url[number_pos+9:number_pos+20]
    return number   
	
@register.filter
def alert(deadline):
    if (deadline - timezone.now()).days < 2 and deadline > timezone.now():
        return True
    else:
        return False

@register.filter
def due(deadline):
    return str(deadline-timezone.now()).split('.')[0]
  
@register.filter
def in_deadline(forum_id, classroom_id):
    try:
        fclass = FClass.objects.get(forum_id=forum_id, classroom_id=classroom_id)
    except ObjectDoesNotExist:
        fclass = FClass(forum_id=forum_id, classroom_id=classroom_id)
    if fclass.deadline:
        if timezone.now() > fclass.deadline_date:
            return fclass.deadline_date
    return ""

@register.filter()
def is_teacher(user_id, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    if user_id == classroom.teacher_id :
      return True
    else:
      return False  

@register.filter()
def is_assistant(user_id, classroom_id):
    assistants = Assistant.objects.filter(classroom_id=classroom_id, user_id=user_id)
    if len(assistants) > 0 :
      return True
    else:
      return False  
    
@register.filter()
def is_pic(title):   
    if title[-3:].upper() == "PNG":
        return True
    if title[-3:].upper() == "JPG":
        return True   
    if title[-3:].upper() == "GIF":
        return True            
    return False    
  
@register.filter()
def likes(work_id):
    sfwork = SFWork.objects.get(id=work_id)
    jsonDec = json.decoder.JSONDecoder()    
    if sfwork.likes:
        like_ids = jsonDec.decode(sfwork.likes)
        return like_ids
    return []  	
	
@register.filter(name='unread') 
def unread(user_id):
    return MessagePoll.objects.filter(reader_id=user_id, read=False).count()    
	
@register.filter
def hash_file(h, key):
    key = int(key)
    if key in h:
      if len(h[key][1])>0:
        return h[key][1][0].filename
      else:
        return "hi"
    else:
      return "no"
	 
@register.filter
def hash_memo(h, key):
    key = int(key)
    if key in h:
      return h[key][0].memo
    else:
      return ""
	  
@register.filter
def hash_score(h, key):
    key = int(key)
    if key in h:
      return h[key][0].score
    else:
      return -1  
    
@register.filter
def hash_date(h, key):
    key = int(key)
    if key in h:
      return h[key][0].publication_date
    else:
      return False
    
@register.filter
def hash_scorer(h, key):
    key = int(key)
    if key in h:
      return h[key][0].scorer
    else:
      return 0

@register.filter
def hash_files(h, key):
    key = int(key)
    if key in h:
      if len(h[key][1])>0:
        return h[key][1]
      else:
        return None
    else:
      return None
	  
@register.filter
def nametoseat(name):
    number = name[-2:]
    if number.isdigit():
        number = int(number)
    else :
        number = 99
    return number	
	
@register.filter(name='week') 
def week(date_number):
    year = date_number // 10000
    month = (date_number - year * 10000) // 100
    day = date_number - year * 10000 - month * 100
    now = datetime(year, month, day, 8, 0, 0)
    return now.strftime("%A")  
	
@register.filter()
def classroom(user_id):
    if user_id > 0 :
        enrolls = Enroll.objects.filter(student_id=user_id).order_by("-id")
        if len(enrolls) > 0 :
            classroom_name = Classroom.objects.get(id=enrolls[0].classroom_id).name
        else :
            classroom_name = ""
        return classroom_name
    else : 
        return "匿名"
		
@register.filter()
def username(user_id):
    user = User.objects.get(id=user_id)
    return user.username

@register.filter(name='abs_filter')
def abs_filter(value):
    return abs(value)

@register.filter()
def int_to_str(number):   
    return str(number)

@register.filter(name='classroom_name')
def classroom_name(classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    return classroom.name