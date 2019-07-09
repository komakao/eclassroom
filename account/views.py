from django.shortcuts import render
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login, logout as auth_logout
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import FormView, RedirectView
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from account.forms import *
from student.models import *
from account.models import *
from teacher.models import *
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.utils.timezone import localtime
from django.db.models import Q
from wsgiref.util import FileWrapper
from django.http import HttpResponse
import os
import urllib.request;
from django.utils.encoding import smart_str
from django.conf import settings
from django.apps import apps
from django.core.files.storage import FileSystemStorage
from uuid import uuid4

# 判斷是否為本班同學
def is_classmate(user_id, classroom_id):
    return Enroll.objects.filter(student_id=user_id, classroom_id=classroom_id).exists()

def is_assistant(user, classroom_id):
    assistants = Assistant.objects.filter(classroom_id=classroom_id, user_id=user.id)
    if len(assistants)>0 :
        return True
    return False
	
# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    if Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists():
        return True
    elif Assistant.objects.filter(user_id=user.id, classroom_id=classroom_id).exists():
        return True
    return False
	
def in_teacher_group(user):
    if not user.groups.filter(name='teacher').exists():
        if not Assistant.objects.filter(user_id=user.id).exists():
            return False
    return True

# 判斷可否觀看訊息
def line_can_read(message_id, user_id):
    if MessagePoll.objects.filter(message_id=message_id, reader_id=user_id).exists():
        return True
    elif Message.objects.filter(id=message_id, author_id=user_id).exists():
        return True
    else:
        return False

# 網站首頁
def homepage(request):
    models = apps.get_models()
    row_count = 0
    for model in models:
        row_count = row_count + model.objects.count()
    users = User.objects.all()
    try :
        admin_user = User.objects.get(id=1)
        admin_profile = Profile.objects.get(user=admin_user)
        admin_profile.home_count = admin_profile.home_count + 1
        admin_profile.save()
    except ObjectDoesNotExist:
        admin_profile = ""
    classroom_count = Classroom.objects.all().count()
    teacher = User.objects.filter(groups__name='teacher').count()
    student = Enroll.objects.values('student_id').distinct().count()
    works = Work.objects.all().count()	
    return render(request, 'homepage.html', {'teacher':teacher, 'student':student, 'works':works, 'classroom_count':classroom_count, 'row_count':row_count, 'user_count':len(users), 'admin_profile': admin_profile})
		
		
class Login(FormView):
    success_url = '/account/dashboard/0'
    form_class = LoginForm
    template_name = "login.html"

    def form_valid(self, form):         
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']         
        if self.kwargs['role'] == 0:	
            user = authenticate(username=username, password=password)
        else:
            teacher = form.cleaned_data['teacher']					
            user = authenticate(username=teacher+"_"+username, password=password)   
        if user is not None:
            auth_login(self.request, user)
        else :
            return redirect("/account/login/"+str(self.kwargs['role']))
        if user.id == 1 and user.first_name == "":          
            user.first_name = "管理員"
            user.save()
			
            try :
                group = Group.objects.get(name="apply")	
            except ObjectDoesNotExist :
                group = Group(name="apply")
                group.save()
            group.user_set.add(user)				
            
            # create Message
            title = "請修改您的暱稱"
            url = "/account/adminname/" + str(self.request.user.id)
            message = Message(title=title, url=url, time=timezone.now())
            message.save()     

            # message for group member
            messagepoll = MessagePoll(message_id = message.id,reader_id=1)
            messagepoll.save() 

            # create Message
            title = "請修改您的密碼"
            url = "/account/password/1/0"
            message = Message(title=title, url=url, time=timezone.now())
            message.save()                                    

            # message for group member
            messagepoll = MessagePoll(message_id = message.id,reader_id=1)
            messagepoll.save() 														
        # 記錄訪客資訊
        admin_user = User.objects.get(id=1)
        try:
            profile = Profile.objects.get(user=admin_user)
        except ObjectDoesNotExist:
            profile = Profile(user=admin_user)
            profile.save()
        profile.visitor_count = profile.visitor_count + 1
        profile.save()
                                    
        year = localtime(timezone.now()).year
        month =  localtime(timezone.now()).month
        day =  localtime(timezone.now()).day
        date_number = year * 10000 + month*100 + day
        try:
            visitor = Visitor.objects.get(date=date_number)
        except ObjectDoesNotExist:
            visitor = Visitor(date=date_number)
        visitor.count = visitor.count + 1
        visitor.save()
                                        
        visitorlog = VisitorLog(visitor_id=visitor.id, user_id=user.id)
        visitorlog.save()                 
          
        # If the test cookie worked, go ahead and
        # delete it since its no longer needed
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

        return super(Login, self).form_valid(form)

    def get_form_class(self):
        if self.kwargs['role'] == 0:
            return LoginForm
        else :
            return LoginStudentForm

class Logout(RedirectView):
    url = '/account/login/0'

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return super(Logout, self).get(request, *args, **kwargs)
		
class SuperUserRequiredMixin(object):  
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("/account/login/0")
        return super(SuperUserRequiredMixin, self).dispatch(request,
            *args, **kwargs)

class UserList(SuperUserRequiredMixin, generic.ListView):
    model = User
    ordering = ['-id']
    paginate_by = 25
	
    def get_queryset(self):
        if self.request.GET.get('account') != None:
            keyword = self.request.GET.get('account')
            if self.kwargs['group'] == 1:
                queryset = User.objects.filter(Q(groups__name='apply') & (Q(username__icontains=keyword) | Q(first_name__icontains=keyword))).order_by("-id")
            else :
                queryset = User.objects.filter(Q(username__icontains=keyword) | Q(first_name__icontains=keyword)).order_by('-id')		
        else :
            if self.kwargs['group'] == 1:
                queryset = User.objects.filter(groups__name='apply').order_by("-id")
            else :
                queryset = User.objects.all().order_by('-id')
        return queryset
	
    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context['group'] = self.kwargs['group']
        return context	     	

def account_detail(request, user_id):
    user = User.objects.get(id=user_id)
    profile = Profile.objects.get(user=user)
    point = profile.work + profile.assistant + profile.forum + profile.like + profile.reply
    return render(request, 'account/user_detail.html', {'user':user, 'profile': profile, 'point':round(point,1)}) 	
	
    
class UserCreate(CreateView):
    model = User
    form_class = UserRegistrationForm
    success_url = "/account/login/0"   
    template_name = 'form.html'
      
    def form_valid(self, form):
        valid = super(UserCreate, self).form_valid(form)
        new_user = form.save(commit=False)
        new_user.first_name = new_user.username
        new_user.set_password(form.cleaned_data.get('password'))
        new_user.save()
        try :
            group = Group.objects.get(name="apply")	
        except ObjectDoesNotExist :
            group = Group(name="apply")
        group.save()
        group.user_set.add(new_user)			
        profile = Profile(user=new_user)
        profile.save()		
        return valid

class UserUpdate(SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    success_url = "/account/user/1"   
    template_name = 'form.html'
    
class UserPasswordUpdate(SuperUserRequiredMixin, UpdateView):
    model = User
    form_class = UserPasswordForm
    success_url = "/account/user/1"   
    template_name = 'form.html'
    
    def form_valid(self, form):
        valid = super(UserPasswordUpdate, self).form_valid(form)
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data.get('password'))
        new_user.save()  
        return valid   

class UserTeacher(SuperUserRequiredMixin, FormView):
    success_url = '/account/user'
    form_class = UserTeacherForm
    template_name = "form.html"
      
    def form_valid(self, form):
        valid = super(UserTeachers, self).form_valid(form)
        user = User.objects.get(id=self.kwargs['pk'])
        try :
            group = Group.objects.get(name="teacher")	
        except ObjectDoesNotExist :
            group = Group(name="teacher")
            group.save()        
        if form.cleaned_data.get('teacher') :
            group.user_set.add(user)
        else: 
            group.user_set.remove(user)
        return valid  
      
    def get_form_kwargs(self):
        kwargs = super(UserTeacher, self).get_form_kwargs()
        kwargs.update({'pk': self.kwargs['pk']})
        return kwargs

		
# Ajax 設為教師、取消教師
def make(request):
    user_id = request.POST.get('userid')
    action = request.POST.get('action')
    if user_id and action :
        user = User.objects.get(id=user_id)           
        try :
            group = Group.objects.get(name="teacher")	
        except ObjectDoesNotExist :
            group = Group(name="teacher")
            group.save()
        if action == 'set':                                  
            group.user_set.add(user)
            # create Message
            title = "<" + request.user.first_name + u">設您為教師"
            url = "/teacher/classroom"
            #message = Message.create(title=title, url=url, time=timezone.now())
            #message.save()                        
                    
            # message for group member
            #messagepoll = MessagePoll.create(message_id = message.id,reader_id=user_id)
            #messagepoll.save()    
        else :   
            group.user_set.remove(user)  
            # create Message
            title = "<"+ request.user.first_name + u">取消您為教師"
            url = "/"
            #message = Message.create(title=title, url=url, time=timezone.now())
            #message.save()                        
                    
            # message for group member
            #messagepoll = MessagePoll.create(message_id = message.id,reader_id=user_id)
            #messagepoll.save()               
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':user_id}, safe=False)               
      
# 列出所有私訊
class LineListView(ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'account/line_list.html'    
    paginate_by = 20
    
    def get_queryset(self):     
        queryset = Message.objects.filter(author_id=self.request.user.id).order_by("-id")
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LineListView, self).get_context_data(**kwargs)
        return context	 
        
# 列出同學以私訊
class LineClassListView(ListView):
    model = Enroll
    context_object_name = 'enrolls'
    template_name = 'account/line_class.html'   
    
    def get_queryset(self):     
        queryset = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("seat")
        return queryset
        
    # 限本班同學
    def render(request, self, context):
        if not is_classmate(self.request.user.id, self.kwargs['classroom_id']):
            return redirect('/')
        return super(LineClassListView, self).render(request, context)            
                
#新增一個私訊
class LineCreateView(CreateView):
    model = Message
    context_object_name = 'messages'    
    form_class = LineForm
    template_name = 'account/line_form.html'     

    def form_valid(self, form):
        self.object = form.save(commit=False)
        user_name = User.objects.get(id=self.request.user.id).first_name
        self.object.title = u"[私訊]" + user_name + ":" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.reader_id = self.kwargs['user_id']
        self.object.type = 2
        self.object.save()
        self.object.url = "/account/line/detail/" + str(self.kwargs['classroom_id']) + "/" + str(self.object.id)
        self.object.classroom_id = 0 - int(self.kwargs['classroom_id'])
        self.object.save()
        if self.request.FILES:
            for file in self.request.FILES.getlist('files'):
                content = MessageContent()
                fs = FileSystemStorage(settings.BASE_DIR + "/static/attach/"+str(self.request.user.id)+"/")
                filename = uuid4().hex
                content.title = file.name
                content.message_id = self.object.id
                content.filename = str(self.request.user.id)+"/" + filename
                fs.save(filename, file)
                content.save()
        # 訊息
        messagepoll = MessagePoll(message_id=self.object.id, reader_id=self.kwargs['user_id'], message_type=2, classroom_id=0-int(self.kwargs['classroom_id']))
        messagepoll.save()              
        return redirect("/account/line/")      
        
    def get_context_data(self, **kwargs):
        context = super(LineCreateView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs['user_id']
        context['classroom_id'] = self.kwargs['classroom_id']
        messagepolls = MessagePoll.objects.filter(reader_id=self.kwargs['user_id'],  classroom_id=0 - int(self.kwargs['classroom_id'])).order_by('-id')
        messages = []
        for messagepoll in messagepolls:
            message = Message.objects.get(id=messagepoll.message_id)
            if message.author_id == self.request.user.id :
                messages.append([message, messagepoll.read])
        context['messages'] = messages
        return context	 
        
#回覆一個私訊
class LineReplyView(CreateView):
    model = Message
    context_object_name = 'messages'    
    form_class = LineForm
    template_name = 'account/line_form_reply.html'     

    def form_valid(self, form):
        self.object = form.save(commit=False)
        user_name = User.objects.get(id=self.request.user.id).first_name
        self.object.title = u"[私訊]" + user_name + ":" + self.object.title
        self.object.author_id = self.request.user.id
        self.object.reader_id = self.kwargs['user_id']
        self.object.type = 2
        self.object.save()
        self.object.url = "/account/line/detail/" + self.kwargs['classroom_id'] + "/" + str(self.object.id)
        self.object.classroom_id = 0 - int(self.kwargs['classroom_id'])
        self.object.save()
        if self.request.FILES:
            for file in self.request.FILES.getlist('files'):
                content = MessageContent()
                fs = FileSystemStorage(settings.BASE_DIR + "/static/attach/"+str(self.request.users.id)+"/")
                filename = uuid4().hex
                content.title = file.name
                content.message_id = self.object.id
                content.filename = str(self.request.user.id)+"/"+filename
                fs.save(filename, file)
                content.save()
        # 訊息
        messagepoll = MessagePoll(message_id=self.object.id, reader_id=self.kwargs['user_id'], message_type=2, classroom_id=0-int(self.kwargs['classroom_id']))
        messagepoll.save()              
        return redirect("/account/line/")      
        
    def get_context_data(self, **kwargs):
        context = super(LineReplyView, self).get_context_data(**kwargs)
        context['user_id'] = self.kwargs['user_id']
        context['classroom_id'] = self.kwargs['classroom_id']
        message = Message.objects.get(id=self.kwargs['message_id'])
        title = "RE:" + message.title[message.title.find(":")+1:]
        context['title'] = title
        messagepolls = MessagePoll.objects.filter(reader_id=self.kwargs['user_id'],  classroom_id=0 - int(self.kwargs['classroom_id'])).order_by('-id')
        messages = []
        for messagepoll in messagepolls:
            message = Message.objects.get(id=messagepoll.message_id)
            if message.author_id == self.request.user.id :
                messages.append([message, messagepoll.read])
        context['messages'] = messages
        return context	 
			
# 查看私訊內容
def line_detail(request, classroom_id, message_id):
    message = Message.objects.get(id=message_id)
    files = MessageContent.objects.filter(message_id=message_id)
    messes = Message.objects.filter(author_id=message.author_id, reader_id=message.reader_id).order_by("-id")
    try:
        if message.type == 2:
            messagepoll = MessagePoll.objects.get(message_id=message_id)
        else:
            messagepoll = MessagePoll.objects.get(message_id=message_id, reader_id=request.user.id)
        if request.user.id == messagepoll.reader_id:
            messagepoll.read = True
        messagepoll.save()
    except :
        messagepoll = MessagePoll()
    canread = line_can_read(message_id, request.user.id)
    return render(request, 'account/line_detail.html', {'canread':canread, 'files':files, 'lists':messes, 'classroom_id':classroom_id, 'message':message, 'messagepoll':messagepoll})

# 下載檔案
def line_download(request, file_id):
    content = MessageContent.objects.get(id=file_id)
    filename = content.title

    download =  settings.BASE_DIR + "/static/upload/" + content.filename
    wrapper = FileWrapper(open(download,"rb"))
    response = HttpResponse(wrapper, content_type = 'application/force-download')
    browser = request.META['HTTP_USER_AGENT'].lower()
    if 'webkit' in browser:
        # Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
        filename_header = 'filename=%s' % filename.encode('utf-8').decode('ISO-8859-1')
		
    elif 'trident' in browser or 'msie' in browser:
        # IE does not support internationalized filename at all.
        # It can only recognize internationalized URL, so we do the trick via routing rules.
        response['Content-Disposition'] = 'attachment; filename='+filename.encode("BIG5").decode("ISO-8859-1")
        return response
    else:
        # For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
        filename_header = 'filename*="utf8\'\'' + str(filename.encode('utf-8').decode('ISO-8859-1')) + '"'
    #response['Content-Disposition'] = 'attachment; filename='+filename.encode("BIG5").decode("ISO-8859-1")
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response
	
# 顯示圖片
def line_showpic(request, file_id):
        content = MessageContent.objects.get(id=file_id)
        return render(request, 'student/forum_showpic.html', {'content':content})
	
class UserDetail(LoginRequiredMixin, generic.DetailView):
    model = User
    
    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs['pk'])
        try:
            profile = Profile.objects.get(user=user)
        except ObjectDoesNotExist:
            profile = Profile(user=user)
            profile.save()
        context['profile'] = profile
        return context
		
# 訊息
class MessageList(LoginRequiredMixin,ListView):
    context_object_name = 'messages'
    paginate_by = 20
    template_name = 'dashboard.html'

    def get_queryset(self):             
        query = []
        #公告
        if self.kwargs['action'] == 1:
            messagepolls = MessagePoll.objects.filter(reader_id=self.request.user.id, message_type=1).order_by('-message_id')
        #私訊
        elif self.kwargs['action'] == 2:
            messagepolls = MessagePoll.objects.filter(reader_id=self.request.user.id, message_type=2).order_by('-message_id')
        #系統
        elif self.kwargs['action'] == 3:
            messagepolls = MessagePoll.objects.filter(reader_id=self.request.user.id, message_type=3).order_by('-message_id')						
        else :
            messagepolls = MessagePoll.objects.filter(reader_id=self.request.user.id).order_by('-message_id')
        for messagepoll in messagepolls:
            query.append([messagepoll, messagepoll.message])
        return query
        
    def get_context_data(self, **kwargs):
        context = super(MessageList, self).get_context_data(**kwargs)
        context['action'] = self.kwargs['action']
        return context
		
def avatar(request):
    profile = Profile.objects.get(user = request.user)      
    return render(request, 'avatar.html', {'avatar':profile.avatar})
	
# 修改真實姓名
def adminnickname(request, user_id):
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.first_name =form.cleaned_data['first_name']
            user.save()
                
            return redirect('/')
    else:
        if request.user.id == user_id:
            user = User.objects.get(id=user_id)
            form = NicknameForm(instance=user)
        else:
            return redirect("/")

    return render(request, 'form.html',{'form': form})
    
# 修改暱稱
def nickname(request, user_id, classroom_id):
    if not request.user.id == user_id :
        if not is_teacher(request.user, classroom_id) or not is_assistant(request.user, classroom_id):
            if not Enroll.objects.filter(classroom_id=classroom_id, student_id=user_id).exists():
               return redirect("/")
    if request.method == 'POST':
        form = NicknameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.first_name =form.cleaned_data['first_name']
            user.save()
                
            return redirect('/')
    else:
        user = User.objects.get(id=user_id)
        form = NicknameForm(instance=user)

    return render(request, 'form.html',{'form': form})
	
def message(request, messagepoll_id):
    messagepoll = MessagePoll.objects.get(id=messagepoll_id)
    messagepoll.read = True
    messagepoll.save()
    message = Message.objects.get(id=messagepoll.message_id)
    return redirect(message.url)
	
# 修改密碼
def password(request, user_id, classroom_id):
    if not request.user.id == user_id :
        if not is_teacher(request.user, classroom_id) or not is_assistant(request.user, classroom_id):
            if not Enroll.objects.filter(classroom_id=classroom_id, student_id=user_id).exists():
               return redirect("/")
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.set_password(request.POST['password'])
            user.save()
               
            return redirect('/')
    else:
        form = PasswordForm()
        user = User.objects.get(id=user_id)

    return render(request, 'form.html',{'form': form, 'user':user})

# 列出所有日期訪客
class VisitorListView(ListView):
    model = Visitor
    context_object_name = 'visitors'
    template_name = 'account/statics_login.html'    
    paginate_by = 20
    
    def get_queryset(self):       
        visitors = Visitor.objects.all().order_by('-id')
        queryset = []
        for visitor in visitors:
            queryset.append([int(str(visitor.date)[0:4]), int(str(visitor.date)[4:6]),int(str(visitor.date)[6:8]),visitor])
        return queryset

    def get_context_data(self, **kwargs):
        context = super(VisitorListView, self).get_context_data(**kwargs)
        first_element = Visitor.objects.all().order_by("-id")[0]
        end_year = int(str(first_element.date)[0:4])
        last_element = Visitor.objects.all().order_by("id")[0]
        start_year = int(str(last_element.date)[0:4])
        context['height'] = 200+ (end_year-start_year)*200
        visitors = Visitor.objects.all().order_by('id')
        queryset = []
        for visitor in visitors:
            queryset.append([int(str(visitor.date)[0:4]), int(str(visitor.date)[4:6]),int(str(visitor.date)[6:8]),visitor])
        context['total_visitors'] = queryset
        return context	
            
# 列出單日日期訪客
class VisitorLogListView(SuperUserRequiredMixin, ListView):
    model = VisitorLog
    context_object_name = 'visitorlogs'
    template_name = 'account/statics_login_log.html'    
    paginate_by = 50
    
    def get_queryset(self):
        # 記錄系統事件
        visitor = Visitor.objects.get(id=self.kwargs['visitor_id'])    
        queryset = VisitorLog.objects.filter(visitor_id=self.kwargs['visitor_id']).order_by('-id')
        return queryset
        
    def render(request, self, context):
        if not self.request.user.is_authenticated():
            return redirect('/')
        return super(VisitorLogListView, self).render(request, context)	