from django.shortcuts import render, redirect
from teacher.models import *
from student.models import *
from student.forms import *
from student.lesson import *
from account.avatar import *
from django.views import generic
from django.contrib.auth.models import User, Group
from django.views.generic import CreateView, UpdateView, DeleteView, ListView, RedirectView, TemplateView
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import IntegrityError
from account.models import *
from account.forms import LineForm
from django.contrib.auth.mixins import LoginRequiredMixin
from collections import OrderedDict
from django.core.files.storage import FileSystemStorage
from uuid import uuid4
from django.contrib.auth.decorators import login_required
import jieba
import json
from django.db.models import Q
from django.http import JsonResponse
import time
from datetime import date
from io import StringIO
import io
from django.core.files.storage import FileSystemStorage
from wsgiref.util import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings

def filename_browser(request, filename):
	browser = request.META['HTTP_USER_AGENT'].lower()
	if 'edge' in browser:
		response['Content-Disposition'] = 'attachment; filename='+urlquote(filename)+'; filename*=UTF-8\'\'' + urlquote(filename)
		return response			
	elif 'webkit' in browser:
		# Safari 3.0 and Chrome 2.0 accepts UTF-8 encoded string directly.
		filename_header = 'filename=%s' % filename.encode('utf-8').decode('ISO-8859-1')
	elif 'trident' in browser or 'msie' in browser:
		# IE does not support internationalized filename at all.
		# It can only recognize internationalized URL, so we do the trick via routing rules.
		filename_header = 'filename='+filename.encode("BIG5").decode("ISO-8859-1")					
	else:
		# For others like Firefox, we follow RFC2231 (encoding extension in HTTP headers).
		filename_header = 'filename*="utf8\'\'' + str(filename.encode('utf-8').decode('ISO-8859-1')) + '"'
	return filename_header		


# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    if Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists():
        return True
    elif Assistant.objects.filter(user_id=user.id, classroom_id=classroom_id).exists():
        return True
    return False
	
# 判斷是否為同班同學
def is_classmate(user, classroom_id):
    enroll_pool = [enroll for enroll in Enroll.objects.filter(classroom_id=classroom_id).order_by('seat')]
    student_ids = map(lambda a: a.student_id, enroll_pool)
    classroom = Classroom.objects.get(id=classroom_id)
    if not classroom.online and not is_teacher(user, classroom_id):
        return False
    if user.id in student_ids:
        return True
    else:
        return False		

class ClassmateRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if 'classroom_id' in kwargs:
            classroom_id = self.kwargs['classroom_id']
        else:
            classroom_id = self.kwargs['pk']
        user = self.request.user
        jsonDec = json.decoder.JSONDecoder()	
        classroom_list = []
        profile = Profile.objects.get(user=user)
        classroom = Classroom.objects.get(id=classroom_id)
        if len(profile.classroom) > 0 :		
            classroom_list = jsonDec.decode(profile.classroom)
        if not classroom.online and not is_teacher(self.request.user, classroom_id):
            return redirect("/")
        if str(classroom_id) in classroom_list :
            return super(ClassmateRequiredMixin, self).dispatch(request,*args, **kwargs)
        else :
            return redirect('/')
		
		
class ClassroomList(LoginRequiredMixin,generic.ListView):
    model = Classroom
    paginate_by = 30 
    ordering = ['-id']	
    template_name = 'student/classroom_list.html'
	
    def get_queryset(self):
        enroll_pool = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = map(lambda a: a.classroom_id, enroll_pool)
        classrooms = Classroom.objects.filter(id__in=classroom_ids).order_by("-id")
        return classrooms
        		

class ClassroomJoinList(LoginRequiredMixin,generic.ListView):
    model = Classroom
    context_object_name = 'queryset'	
    paginate_by = 30  	
    template_name = 'student/classroom_join.html'    
    
    def get_queryset(self):
        queryset = []
        enrolls = Enroll.objects.filter(student_id=self.request.user.id)
        classroom_ids = list(map(lambda a: a.classroom_id, enrolls))     
        teacher_username = self.request.user.username.split("_")[0]
        try:
            teacher_id = User.objects.get(username=teacher_username).id
        except ObjectDoesNotExist:
            teacher_id = 0
        if teacher_id == 0 or self.kwargs['kind'] == 0:
            classrooms = Classroom.objects.all().order_by("-id")
        else:
            classrooms = Classroom.objects.filter(teacher_id=teacher_id).order_by("-id")
        for classroom in classrooms:
            if classroom.id in classroom_ids:
                queryset.append([classroom, True])
            else:
                queryset.append([classroom, False])
        return queryset
		
    def get_context_data(self, **kwargs):
        context = super(ClassroomJoinList, self).get_context_data(**kwargs)
        context['kind'] = self.kwargs['kind']
        return context 

class ClassroomEnrollCreate(LoginRequiredMixin,CreateView):
    model = Enroll
    form_class = EnrollForm    
    template_name = "form.html"
    
    def form_valid(self, form):
        valid = form.save(commit=False)
        if form.cleaned_data['password'] == Classroom.objects.get(id=self.kwargs['pk']).password:
            enroll = Enroll(student_id=self.request.user.id, classroom_id=self.kwargs['pk'], seat=form.cleaned_data['seat'], computer=form.cleaned_data['computer'])
            try:
                enroll.save()
            except:
                pass
        try :
            group = Group.objects.get(name="class"+str(self.kwargs['pk']))	
        except ObjectDoesNotExist :
            group = Group(name="class"+str(self.kwargs['pk']))
            group.save()     
        group.user_set.add(self.request.user)				
        jsonDec = json.decoder.JSONDecoder()	
        classroom_list = []
        user = self.request.user
        profile = Profile.objects.get(user=user)
        if len(profile.classroom) > 0 :		
            classroom_list = jsonDec.decode(profile.classroom)
        classroom_list.append(str(self.kwargs['pk']))
        profile.classroom = json.dumps(classroom_list)
        profile.save()		
        classroom = Classroom.objects.get(id=self.kwargs['pk'])
        messages = Message.objects.filter(author_id=classroom.teacher_id, classroom_id=classroom.id, type=1)
        for message in messages:
            try :
                messagepoll = MessagePoll.objects.get(message_type=1, message_id=message.id, reader_id=user.id, classroom_id=classroom.id)
            except ObjectDoesNotExist:
                messagepoll = MessagePoll(message_type=1, message_id=message.id, reader_id=user.id, classroom_id=classroom.id)
                messagepoll.save()
            except MultipleObjectsReturned:
                pass			
        return redirect('/student/group/'+str(self.kwargs['pk']))
		
class ClassmateList(ClassmateRequiredMixin,generic.ListView):
    model = Enroll   
    template_name = 'student/classmate.html'
    
    def get_queryset(self):
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['pk']).order_by("seat")
        return enrolls  

    def get_context_data(self, **kwargs):
        context = super(ClassmateList, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['pk'])
        return context				
      
class ClassroomSeatUpdate(LoginRequiredMixin,UpdateView):
    model = Enroll
    fields = ['seat']
    success_url = "/student/classroom/"      
    template_name = "form.html"
	
class ClassroomComputerUpdate(LoginRequiredMixin,UpdateView):
    model = Enroll
    fields = ['computer']
    success_url = "/student/classroom/"      
    template_name = "form.html"

# 分類課程    
def lessons(request, subject_id): 
        lock = 1
        del lesson_list[:]
        reset()   
        works = Work.objects.filter(typing=0, user_id=request.user.id, lesson=subject_id).order_by("-id")	
        if subject_id == 2 or subject_id == 3:
            for unit, unit1 in enumerate(lesson_list[int(subject_id)-2][1]):
                for index, assignment in enumerate(unit1[1]):
                    if len(works) > 0 :
                        sworks = list(filter(lambda w: w.index==assignment[2], works))
                        if len(sworks)>0 :
                            lesson_list[int(subject_id)-1][1][unit][1][index].append(sworks[0])
                        else :
                            lesson_list[int(subject_id)-1][1][unit][1][index].append(False)
                    else :
                        lesson_list[int(subject_id)-2][1][unit][1][index].append(False)
        elif subject_id == 1:
            if request.user.is_authenticated:
                user_id = request.user.id
                user = User.objects.get(id=user_id)
                profile = Profile.objects.get(user=user)
                lock = profile.lock1
            else :
                user_id = 0
                lock = 1            
        return render(request, 'student/lessons.html', {'subject_id': subject_id, 'lesson_list':lesson_list, 'lock':lock})

# 課程內容
def lesson(request, lesson, unit, index):
        lesson_dict = OrderedDict()
        works = Work.objects.filter(user_id=request.user.id, lesson=lesson, index=index).order_by("-id")
        for unit1 in lesson_list[int(lesson)-2][1]:
            for assignment in unit1[1]:
                sworks = list(filter(lambda w: w.index==assignment[2], works))
                if len(sworks)>0 :
                    lesson_dict[assignment[2]] = [assignment, sworks[0]]
                else :
                    lesson_dict[assignment[2]] = [assignment, None]
        assignment = lesson_dict[int(index)]
        scores = []
        workfiles = []
        #work_index = lesson_list[int(lesson)-1][1][int(unit)-1][1][int(index)-1][2]	
        works = Work.objects.filter(typing=0, index=index, lesson=lesson, user_id=request.user.id)

        if not works.exists():
            form = SubmitAForm()
        else:
            workfiles = WorkFile.objects.filter(work_id=works[0].id).order_by("-id")							
            form = SubmitAForm(instance=works[0])
            if len(workfiles)>0 and works[0].scorer>0: 
                score_name = User.objects.get(id=works[0].scorer).first_name
                scores = [works[0].score, score_name]	
        return render(request, 'student/lesson.html', {'assignment':assignment, 'index':index, 'form': form, 'unit':unit, 'lesson':lesson, 'scores':scores, 'workfiles': workfiles})

def submit(request, typing, lesson, index):
    lesson_dict = OrderedDict()
    work_dict = {}
    work_dict = dict(((int(work.index), [work, WorkFile.objects.filter(work_id=work.id).order_by("-id")]) for work in Work.objects.filter(typing=typing, lesson=lesson, user_id=request.user.id)))
    works = Work.objects.filter(typing=typing, user_id=request.user.id, lesson=lesson, index=index).order_by("-id")
    if typing == 0: 
        for unit in lesson_list[int(lesson)-1][1]:
            for assignment in unit[1]:
                lesson_dict[assignment[2]] = assignment[0]
        assignment = lesson_dict[index]
    elif typing == 1:
        assignment = TWork.objects.get(id=index).title
    scores = []
    workfiles = []
    try:
        filepath = request.FILES['file']
    except :
        filepath = False
    if request.method == 'POST':
        if filepath :
            myfile = request.FILES['file']
            fs = FileSystemStorage(settings.BASE_DIR+"/static/work/"+str(request.user.id)+"/")
            filename = uuid4().hex
            fs.save(filename, myfile)
			
        form = SubmitAForm(request.POST, request.FILES)
        if not works.exists():
            if form.is_valid():
                work = Work(typing=typing, lesson=lesson, index=index, user_id=request.user.id, memo=form.cleaned_data['memo'], publication_date=timezone.now())
                work.save()
                workfile = WorkFile(work_id=work.id, filename=filename)
                workfile.save()
	     		# credit
                update_avatar(request.user.id, 1, 2)
                # History
                history = PointHistory(user_id=request.user.id, kind=1, message='2分--繳交作業<'+assignment+'>', url='/student/work/show/'+str(typing)+'/'+str(lesson)+'/'+str(index)+'/'+str(request.user.id))
                history.save()
        else:
            if form.is_valid():
                works.update(memo=form.cleaned_data['memo'],publication_date=timezone.localtime(timezone.now()))
                workfile = WorkFile(work_id=works[0].id, filename=filename)
                workfile.save()
            else :
                works.update(memo=form.cleaned_data['memo'])           
        return redirect('/student/work/show/'+str(typing)+'/'+str(lesson)+'/'+str(index)+'/'+str(request.user.id))
    else:
        if not works.exists():
            form = SubmitAForm()
        else:
            workfiles = WorkFile.objects.filter(work_id=works[0].id).order_by("-id")							
            form = SubmitAForm(instance=works[0])
            if len(workfiles)>0 and works[0].scorer>0: 
                score_name = User.objects.get(id=works[0].scorer).first_name
                scores = [works[0].score, score_name]	
    return render(request, 'student/submitA.html', {'work_dict':work_dict, 'assignment':assignment, 'index':index, 'form': form, 'lesson':lesson, 'scores':scores, 'workfiles': workfiles})
		
        
# 列出所有作業        
def work(request, typing, classroom_id):
    classroom = Classroom.objects.get(id=classroom_id)
    lesson = classroom.lesson
    lesson_dict = OrderedDict()
    works = Work.objects.filter(typing=typing, user_id=request.user.id, lesson=classroom.lesson).order_by("id")
    group_ids = [group.group_id for group in WorkGroup.objects.filter(typing=typing, classroom_id=classroom_id)] 
    assistant_pool = [assistant for assistant in WorkAssistant.objects.filter(typing=typing, lesson=lesson, classroom_id=classroom_id)]				
	
    if typing == 0:
        lesson = Classroom.objects.get(id=classroom_id).lesson
        if lesson == 1:
            assignments = lesson_list1
            work_dict = dict(((work.index, work) for work in Work.objects.filter(typing=typing, user_id=request.user.id, lesson=lesson)))

            for assignment in assignments:
                sworks = list(filter(lambda w: w.index==assignment[2], works))
                assistant = list(filter(lambda w: (w.index==assignment[2] and w.group==group), assistant_pool))
                if len(sworks)>0 :
                    if len(assistant) > 0:
                        lesson_dict[assignment[0]] = [assignment[1], assignment[2], sworks[0], 0, assistant[0].student_id]
                    else :
                        lesson_dict[assignment[0]] = [assignment[1], assignment[2], sworks[0], 0, 0]                        
                else :
                    lesson_dict[assignment[0]] = [assignment[1],  assignment[2], None, 0]
        elif lesson == 2 or lesson == 3:
            assignments = lesson_list      
            unit_count = 1
            for unit in lesson_list[int(lesson)-2][1]:
                for assignment in unit[1]:
                    try:
                        group_id = WorkGroup.objects.get(classroom_id=classroom_id, index=assignment[2], typing=typing).group_id
                    except ObjectDoesNotExist:
                        group_id = 0
                    enroll_id = Enroll.objects.get(classroom_id=classroom_id, student_id=request.user.id).id
                    try :   
                        studentgroup = StudentGroup.objects.get(enroll_id=enroll_id, group_id=group_id)
                        group = studentgroup.group
                    except ObjectDoesNotExist:
                        group = -1    
                    sworks = list(filter(lambda w: w.index==assignment[2], works))
                    assistant = list(filter(lambda w: (w.index==assignment[2] and w.group==group), assistant_pool))
                    if len(sworks)>0 :
                        if len(assistant) > 0:
                            lesson_dict[assignment[2]] = [unit[0], assignment[0], sworks[0], unit_count, assistant[0].student_id]
                        else :
                            lesson_dict[assignment[2]] = [unit[0], assignment[0], sworks[0], unit_count, 0]                        
                    else :
                         lesson_dict[assignment[2]] = [unit[0], assignment[0], None, unit_count]
			
                unit_count += 1
        return render(request, 'student/work.html', {'typing': typing, 'works':works, 'lesson_dict':lesson_dict.items(), 'user_id': request.user.id, 'classroom':classroom})					
			
    elif typing == 1:
        assignments = TWork.objects.filter(classroom_id=classroom_id)
        for assignment in assignments:
            sworks = list(filter(lambda w: w.index==assignment.id, works))
            assistant = list(filter(lambda w: w.index==assignment.id, assistant_pool))			
            if len(sworks)>0 :
                if len(assistant) > 0:			
                    lesson_dict[assignment.id] = [assignment.title, assignment.id, sworks[0], 0, assistant[0].student_id]
                else:
                    lesson_dict[assignment.id] = [assignment.title, assignment.id, sworks[0], 0, 0]				
            else :
                lesson_dict[assignment.id] = [assignment.title, assignment.id, None, 0]
        return render(request, 'student/work.html', {'typing': typing, 'works':works, 'lesson_dict':sorted(lesson_dict.items()), 'user_id': request.user.id, 'classroom':classroom})					
		
def work_download(request, typing, lesson, index, user_id, workfile_id):
    lesson_dict = OrderedDict()
    if typing == 0:
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2]
        else:
            for unit in lesson_list[int(lesson)-1][1]:
                for assignment in unit[1]:
                    lesson_dict[assignment[2]] = assignment[0]
    elif typing == 1:
        try:
            assignment = TWork.objects.get(id=index)
            lesson_dict[index] = assignment.title
        except ObjectDoesNotExist():
            lesson_dict[index] = ""
 
    workfile = WorkFile.objects.get(id=workfile_id)
    username = User.objects.get(id=user_id).first_name
    #reload(sys)  
    #sys.setdefaultencoding('utf8')		
    filename = username + "_" + lesson_dict[int(index)]  + ".sb3"
    download =  settings.BASE_DIR + "/static/work/" + str(user_id) + "/" + workfile.filename
    wrapper = FileWrapper(open(download, "rb"))
    response = HttpResponse(wrapper, content_type = 'application/force-download')
    #response = HttpResponse(content_type='application/force-download')
    filename_header = filename_browser(request, filename)
    response['Content-Disposition'] = 'attachment; ' + filename_header
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response
    #return render_to_response('student/download.html', {'download':download})
			
	
# 查詢某作業分組小老師    
def work_group(request, typing, lesson, index, classroom_id):
        if not is_classmate(request.user, classroom_id):
            return redirect("/account/login/0")
        student_groups = []
        classroom = Classroom.objects.get(id=classroom_id)

        try:
            group_id = WorkGroup.objects.get(typing=typing, classroom_id=classroom_id, index=index).group_id
        except ObjectDoesNotExist:
            group_id = 0            
        group_id = WorkGroup.objects.get(classroom_id=classroom_id, index=index, typing=typing).group_id
        enroll_id = Enroll.objects.get(classroom_id=classroom_id, student_id=request.user.id).id
        try :
            studentgroup = StudentGroup.objects.get(enroll_id=enroll_id, group_id=group_id)
            group = studentgroup.group
        except ObjectDoesNotExist:
            group = -1  

        lesson = classroom.lesson
        studentgroups = StudentGroup.objects.filter(group_id=group_id, group=group)    
        enroll_ids = map(lambda a: a.enroll_id, studentgroups)                                             
        enrolls = Enroll.objects.filter(id__in=enroll_ids)
        group_assistants = []
        works = []
        scorer_name = ""
        for member in enrolls: 
            enroll = Enroll.objects.get(id=member.id)			
            try:    
                work = Work.objects.get(typing=typing, user_id=enroll.student_id, index=index, lesson=lesson)
                if work.scorer > 0 :
                    scorer = User.objects.get(id=work.scorer)
                    scorer_name = scorer.first_name
                else :
                    scorer_name = "X"
            except ObjectDoesNotExist:
                work = Work(typing=typing, lesson=lesson, index=index, user_id=enroll.student_id, score=-2)
            except MultipleObjectsReturned:
                work = Work.objects.filter(typing=typing, user_id=enroll.student_id, index=index, lesson=lesson).order_by("-id")[0]
            works.append([enroll, work.score, scorer_name, work.file])
            try :
                assistant = WorkAssistant.objects.get(typing=typing, lesson=lesson, index=index, group=group, student_id=enroll.student_id)
                group_assistants.append(enroll)
            except ObjectDoesNotExist:
                pass
            except MultipleObjectsReturned:
                assistants = WorkAssistant.objects.filter(typing=typing, lesson=lesson, index=index, group=group, student_id=enroll.student_id).order_by("-id")
                assistant = assistants[0]
                group_assistants.append(enroll)					
        student_groups.append([group, works, group_assistants])
        if typing == 0:
            lesson_dict = {}
            for unit in lesson_list[int(lesson)-1][1]:
                for assignment in unit[1]:
                    lesson_dict[assignment[2]] = assignment[0]    
            assignment = lesson_dict[int(index)]
        else:
            assignment = TWork.objects.get(id=index).title		
        return render(request, 'student/work_group.html', {'lesson':lesson, 'assignment':assignment, 'student_groups':student_groups, 'classroom_id':classroom_id, 'typing':typing, 'index':index})

def memo(request, typing, classroom_id, index):
    if not is_classmate(request.user, classroom_id):
        return redirect("/account/login/0")
    classroom = Classroom.objects.get(id=classroom_id)
    lesson = classroom.lesson
    enrolls = Enroll.objects.filter(classroom_id=classroom_id)
    datas = []
    for enroll in enrolls:
        try:
            work = Work.objects.get(lesson=lesson, index=index, user_id=enroll.student_id, typing=typing)
            datas.append([enroll, work.memo])
        except ObjectDoesNotExist:
            datas.append([enroll, ""])
        except MultipleObjectsReturned:
            work = Work.objects.filter(lesson=lesson, index=index, user_id=enroll.student_id, typing=typing).order_by("-id")
            datas.append([enroll, work[0].memo])			
    def getKey(custom):
        return custom[0].seat
    datas = sorted(datas, key=getKey)	 
    return render(request, 'student/memo.html', {'typing':typing, 'datas': datas, 'lesson':lesson, 'classroom_id':classroom_id})

# 查詢某班級心得統計
def memo_count(request, typing, classroom_id, index):
        if not is_classmate(request.user, classroom_id):
            return redirect("/account/login/0")
        lesson = Classroom.objects.get(id=classroom_id).lesson
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        members = []
        for enroll in enrolls:
            members.append(enroll.student_id)
        classroom = Classroom.objects.get(id=classroom_id)
        if index == 0 :
            works = Work.objects.filter(typing=typing, lesson=classroom.lesson, user_id__in=members)
        else :
            works = Work.objects.filter(typing=typing, lesson=classroom.lesson, user_id__in=members, index=index)		
        memo = ""
        for work in works:
            memo += " " + work.memo
        memo = memo.rstrip('\r\n')
        seglist = jieba.cut(memo, cut_all=False)
        hash = {}
        for item in seglist: 
            if item in hash:
                hash[item] += 1
            else:
                hash[item] = 1
        words = []
        count = 0
        error=""
        for key, value in sorted(hash.items(), key=lambda x: x[1], reverse=True):
            if ord(key[0]) > 32 :
                count += 1	
                words.append([key, value])
                if count == 30:
                    break        
        return render(request, 'student/memo_count.html', {'typing':typing, 'words':words, 'enrolls':enrolls, 'classroom':classroom, 'index':index})

# 評分某同學某進度心得
@login_required
def memo_user(request, typing, user_id, lesson, classroom_id):
    if not is_classmate(request.user, classroom_id):
        return redirect("/account/login/0")
    user = User.objects.get(id=user_id)
    works = Work.objects.filter(lesson=lesson, user_id=user_id, typing=typing)
    lesson_dict = {}
    if typing == 0:
        for unit in lesson_list[int(lesson)-1][1]:
            for assignment in unit[1]:
                sworks = list(filter(lambda w: w.index==assignment[2], works))
                if len(sworks)>0 :
                    lesson_dict[assignment[2]] = [assignment[0], sworks[0]]
                else :
                    lesson_dict[assignment[2]] = [assignment[0], None]
    else :
        assignments = TWork.objects.filter(classroom_id=classroom_id)
        for assignment in assignments:
            sworks = list(filter(lambda w: w.index==assignment.id, works))
            if len(sworks)>0 :
                lesson_dict[assignment.id] = [assignment.title, sworks[0]]
            else :
                lesson_dict[assignment.id] = [assignment.title, None]		
    return render(request, 'student/memo_user.html', {'typing':typing, 'lesson_dict':sorted(lesson_dict.items()), 'student': user})

# 查詢某班某作業某詞句心得
def memo_word(request, typing, classroom_id, index, word):
        if not is_classmate(request.user, classroom_id):
            return redirect("/account/login/0")
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        members = []
        for enroll in enrolls:
            members.append(enroll.student_id)
        classroom = Classroom.objects.get(id=classroom_id)
        if index == 0 :
            works = Work.objects.filter(typing=typing, lesson=classroom.lesson, user_id__in=members, memo__contains=word)
        else :
            works = Work.objects.filter(typing=typing, lesson=classroom.lesson, user_id__in=members, index=index, memo__contains=word)					
        for work in works:
            work.memo = work.memo.replace(word, '<font color=red>'+word+'</font>')            
        return render(request, 'student/memo_word.html', {'word':word, 'works':works, 'classroom':classroom})
		
		
# 查詢個人心得
def memo_show(request, typing, user_id, unit,classroom_id, score):
    if not is_classmate(request.user, classroom_id):
        return redirect("/account/login/0")
    user_name = User.objects.get(id=user_id).first_name
    lesson = Classroom.objects.get(id=classroom_id).lesson
    works = Work.objects.filter(typing=typing, user_id=user_id, lesson=lesson)
    for work in works:
        lesson_list[work.index-1].append(work.score)
        lesson_list[work.index-1].append(work.publication_date)
        if work.score > 0 :
            score_name = User.objects.get(id=work.scorer).first_name
            lesson_list[work.index-1].append(score_name)
        else :
            lesson_list[work.index-1].append("null")
        lesson_list[work.index-1].append(work.memo)
    c = 0
    for lesson in lesson_list:
        assistant = Assistant.objects.filter(student_id=user_id, lesson=c+1)
        if assistant.exists() :
            lesson.append("V")
        else :
            lesson.append("")
        c = c + 1
        #enroll_group = Enroll.objects.get(classroom_id=classroom_id, student_id=request.user.id).group
    user = User.objects.get(id=user_id)      
    return render(request, 'student/memo_show.html', {'classroom_id': classroom_id, 'works':works, 'lesson_list':lesson_list, 'user_name': user_name, 'unit':unit, 'score':score})

# 查詢作業進度
def progress(request, typing, classroom_id, group_id):
    if not is_classmate(request.user, classroom_id):
        return redirect("/")
    classroom = Classroom.objects.get(id=classroom_id)
    lesson = classroom.lesson
    bars = []
    enrolls = []
    lesson_dict = {}
    enroll = Enroll.objects.get(classroom_id=classroom_id, student_id=request.user.id)    
    classroomgroups = []
    if classroom.progress == 0:
        enrolls = Enroll.objects.filter(classroom_id=classroom_id, student_id=request.user.id)
    elif classroom.progress == 1:
        classroomgroups = ClassroomGroup.objects.filter(classroom_id=classroom_id).order_by("id")
        if len(classroomgroups)> 0 :
            group_id=classroomgroups[0].id
            try:
                studentgroup = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll.id).group
            except ObjectDoesNotExist :
                studentgroup = -1
            studentgroups = StudentGroup.objects.filter(group_id=group_id, group=studentgroup)
            enroll_ids = map(lambda w: w.enroll_id, studentgroups)
            enrolls = Enroll.objects.filter(id__in=enroll_ids)   
    else:
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")	
    if request.user.id == classroom.teacher_id:
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")	        	
    student_ids = map(lambda a: a.student_id, enrolls)	
    work_pool = Work.objects.filter(user_id__in=student_ids, lesson=classroom.lesson, typing=typing)		
    user_groups = ClassroomGroup.objects.filter(classroom_id=classroom_id)
    group_ids = []
    for group in user_groups:        
        if not group.id in group_ids:
            group_ids.append(group.id)
    groups = StudentGroup.objects.filter(group_id__in=group_ids, enroll_id=enroll.id)
    user_group = []
    for group in groups:
        user_group.append(group.group)
    enroll_groups = StudentGroup.objects.filter(group_id__in=group_ids, group__in=user_group)
    enroll_group = []
    enroll_group = map(lambda a: a.enroll_id, enroll_groups)
    if typing == 0:		
        if lesson == 1:
            for assignment in lesson_list1:
                lesson_dict[assignment[3]] = assignment[2]
        elif lesson == 2:		
            for unit in lesson_list[int(classroom.lesson)-2][1]:
                for assignment in unit[1]:
                    lesson_dict[assignment[2]] = assignment[0]
        for enroll in enrolls:
            bars1 = []
            for key, assignment in lesson_dict.items():
                works = list(filter(lambda u: ((u.user_id == enroll.student_id) and (u.index==key)), work_pool))
                if len(works) > 0:
                    bars1.append([enroll, works[0]])
                else :
                    bars1.append([enroll, None]) 
            bars.append(bars1)
    elif typing == 1:
        lessons = TWork.objects.filter(classroom_id=classroom_id)
        for lesson in lessons:
            lesson_dict[lesson.id] = lesson.title	
        for enroll in enrolls:
            bar = []
            for assignment in lessons:		
                works = list(filter(lambda u: ((u.index == assignment.id) and (u.user_id == enroll.student_id)), work_pool))
                if len(works) > 0:
                    bar.append([enroll, works[0]])
                else:
                    bar.append([enroll, False])
            bars.append(bar)
    return render(request, 'student/progress.html', {'group_id':group_id, 'classroomgroups':classroomgroups, 'typing':typing,  'classroom':classroom, 'user_group':enroll_group, 'bars':bars, 'lesson_dict':sorted(lesson_dict.items())})
    
# 所有作業的小老師
def work_groups(request, classroom_id):
        if not is_classmate(request.user, classroom_id):
            return redirect("/")
        lesson = Classroom.objects.get(id=classroom_id).lesson
        group = Enroll.objects.get(student_id=request.user.id, classroom_id=classroom_id).group
        enrolls = Enroll.objects.filter(classroom_id=classroom_id, group=group)
        try:
            group_name = EnrollGroup.objects.get(id=group).name
        except ObjectDoesNotExist:
            group_name = "沒有組別"
        student_ids = map(lambda a: a.student_id, enrolls)	
        assistant_pool = [assistant for assistant in Assistant.objects.filter(student_id__in=student_ids, classroom_id=classroom_id)]				
        work_pool = Work.objects.filter(user_id__in=student_ids, lesson=lesson).order_by("id")					
        lessons = []		
        lesson_dict = OrderedDict()
        for unit1 in lesson_list[int(lesson)-1][1]:
            for assignment in unit1[1]:               
                members = filter(lambda u: u.group == group, enrolls)								
                student_group = []
                group_assistants = []
                for enroll in members:
                    sworks = filter(lambda w:(w.index==assignment[2] and w.user_id==enroll.student_id), work_pool)
                    if len(sworks) > 0:
                        student_group.append([enroll, sworks[0]])
                    else :
                        student_group.append([enroll, None])
                    assistant = filter(lambda a: a.student_id == enroll.student_id and a.lesson == assignment[2], assistant_pool)
                    if assistant:
                        group_assistants.append(enroll)												
                lesson_dict[assignment[2]] = [assignment, student_group, group_assistants, group_name]
        return render(request, 'student/work_groups.html', {'lesson_dict':sorted(lesson_dict.iteritems()), 'classroom_id':classroom_id})
 						
						
# 列出所有公告
class AnnounceListView(ClassmateRequiredMixin, ListView):
    model = Message
    context_object_name = 'messages'
    template_name = 'student/announce_list.html'    
    paginate_by = 20
    
    def get_queryset(self):
        classroom = Classroom.objects.get(id=self.kwargs['classroom_id'])  
        messages = Message.objects.filter(classroom_id=classroom.id, author_id=classroom.teacher_id, type=1).order_by("-id")
        queryset = []
        for message in messages:
            try: 
                messagepoll = MessagePoll.objects.get(message_id=message.id, reader_id=self.request.user.id, classroom_id=classroom.id, message_type=1)
                queryset.append([messagepoll, message])
            except ObjectDoesNotExist :
                messagepoll = "2"
            except MultipleObjectsReturned:
                messagepoll = MessagePoll.objects.filter(message_id=message.id, reader_id=self.request.user.id, classroom_id=classroom.id, message_type=1)[0]
                queryset.append([messagepoll, message])
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(AnnounceListView, self).get_context_data(**kwargs)
        context['classroom'] = Classroom.objects.get(id=self.kwargs['classroom_id'])
        return context	    						
		
# 列出所有討論主題
class ForumList(ClassmateRequiredMixin, ListView):
    model = SFWork
    context_object_name = 'works'
    template_name = 'student/forum_list.html'    
    
    def get_queryset(self):
        queryset = []
        fclass_dict = dict(((fclass.forum_id, fclass) for fclass in FClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))	
        #fclasses = FClass.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        fworks = FWork.objects.filter(id__in=fclass_dict.keys()).order_by("-id")
        sfwork_pool = SFWork.objects.filter(student_id=self.request.user.id).order_by("-id")
        for fwork in fworks:
            sfworks = list(filter(lambda w: w.index==fwork.id, sfwork_pool))
            if len(sfworks)> 0 :
                queryset.append([fwork, sfworks[0].publish, fclass_dict[fwork.id], len(sfworks)])
            else :
                queryset.append([fwork, False, fclass_dict[fwork.id], 0])
        def getKey(custom):
            return custom[2].publication_date, custom[2].forum_id
        queryset = sorted(queryset, key=getKey, reverse=True)	
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(ForumList, self).get_context_data(**kwargs)
        context['classroom_id'] = self.kwargs['classroom_id']
        context['bookmark'] =  self.kwargs['bookmark']
        context['fclasses'] = dict(((fclass.forum_id, fclass) for fclass in FClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))
        return context	    

    # 限本班同學
    def render_to_response(self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        return super(ForumList, self).render_to_response(context)    

class ForumPublish(TemplateView):
    template_name = "student/forum_publish.html"

class ForumPublishDone(ClassmateRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
      index = self.kwargs['index']
      classroom_id = self.kwargs['classroom_id']
      user_id = self.request.user.id
      try:
          fwork = FWork.objects.get(id=index)
          works = SFWork.objects.filter(index=index, student_id=user_id).order_by("-id")
          work = works[0]
          work.publish = True
          work.save()
          if len(works) == 1:
            update_avatar(self.request.user.id, 4, 2)
            # History
            history = PointHistory(user_id=self.request.user.id, kind=4, message=u'2分--繳交討論區作業<'+fwork.title+'>', url='/student/forum/memo/'+str(classroom_id)+'/'+str(index)+'/0')
            history.save()								
      except ObjectDoesNotExist:
            pass
      return "/student/forum/memo/"+str(classroom_id)+"/"+str(index)+"/0"
  
 	
class ForumSubmit(ClassmateRequiredMixin, CreateView):
    model = SFWork
    form_class = ForumSubmitForm    
    template_name = "student/forum_form.html"
    
    def form_valid(self, form):
        valid = super(ForumSubmit, self).form_valid(form)
        index = self.kwargs['index']
        user_id = self.request.user.id
        work = SFWork(index=index, student_id=user_id, publish=False)
        work.memo = form.cleaned_data['memo']
        work.memo_e = form.cleaned_data['memo_e']
        work.memo_c = form.cleaned_data['memo_c']								
        work.save()
        if self.request.FILES:
            content = SFContent(index=index, student_id=user_id)
            myfile =  self.request.FILES.get("file", "")
            fs = FileSystemStorage()
            filename = uuid4().hex
            content.title = myfile.name
            content.work_id = work.id
            content.filename = str(user_id)+"/"+filename
            fs.save("static/upload/"+str(user_id)+"/"+filename, myfile)
            content.save()
        return valid
            
    def get_success_url(self):
        index = self.kwargs['index']
        user_id = self.request.user.id
        classroom_id = self.kwargs['classroom_id']
        works = SFWork.objects.filter(index=index, student_id=user_id).order_by("-id")        
        if not works:
            succ_url = "/student/forum/publish/"+str(classroom_id)+"/"+str(index)	
        elif not works[0].publish:
            succ_url = "/student/forum/publish/"+str(classroom_id)+"/"+str(index)
        else :
            succ_url = "/student/forum/memo/"+str(classroom_id)+"/"+str(index)+"/0"
        return succ_url            

    def get_context_data(self, **kwargs):
        context = super(ForumSubmit, self).get_context_data(**kwargs)
        index = self.kwargs['index']
        classroom_id = self.kwargs['classroom_id']
        user_id = self.request.user.id
        context['classroom_id'] = classroom_id
        context['subject'] =  FWork.objects.get(id=index).title
        context['files'] = SFContent.objects.filter(index=index, student_id=user_id,visible=True).order_by("-id")
        context['index'] = index
        context['fwork'] = FWork.objects.get(id=index)
        works = SFWork.objects.filter(index=index, student_id=user_id).order_by("-id")
        if not works.exists():
            work = SFWork(index=0, publish=False)
        else:
            work = works[0]
        context['works'] = works
        context['work'] = work
        context['scores'] = []
        context['contents'] = FContent.objects.filter(forum_id=index).order_by("id")
        return context	           

class ForumShow(ClassmateRequiredMixin, ListView):
  	model = FContent
  	context_object_name = 'contents'
  	template_name = 'student/forum_show.html'    
    
  	def get_queryset(self): 
  		contents = FContent.objects.filter(forum_id=self.kwargs['index']).order_by("id")
  		return contents
    
  	def get_context_data(self, **kwargs):
  		context = super(ForumShow, self).get_context_data(**kwargs)      
  		index = self.kwargs['index']
  		user_id = self.kwargs['user_id']
  		classroom_id = self.kwargs['classroom_id']
  		forum = FWork.objects.get(id=index)
  		teacher_id = forum.teacher_id
  		work = []
  		replys = []
  		files = []
  		works = SFWork.objects.filter(index=index, student_id=user_id).order_by("-id")
	  	publish = False
  		if len(works)> 0:
  			work_new = works[0]
  			work_first = works.last()
  			publish = work_first.publish
  			replys = SFReply.objects.filter(index=index, work_id=work_first.id).order_by("-id")	
  			files = SFContent.objects.filter(index=index, student_id=user_id, visible=True).order_by("-id")	
  		else :
  			work_new = SFWork(index=index, student_id=user_id)
  			work_first = SFWork(index=index, student_id=user_id)			
  		context['work_new'] = work_new
  		context['work_first'] = work_first
  		context['publish'] = publish
  		context['classroom_id'] = classroom_id
  		context['replys'] = replys
  		context['files'] = files
  		context['index'] = index
  		context['forum'] = forum
  		context['user_id'] = user_id
  		context['teacher_id'] = teacher_id
  		context['works'] = works
  		context['is_teacher'] = is_teacher(self.request.user, classroom_id)
  		return context

    # 限本班同學
  	def render_to_response(self, context):
  		try:
  		  enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
  		except ObjectDoesNotExist :
  		  return redirect('/')
  		return super(ForumShow, self).render_to_response(context)      
    
 # 查詢某作業所有同學心得
class ForumMemo(ClassmateRequiredMixin, ListView):
    model = SFWork
    context_object_name = 'contents'
    template_name = 'student/forum_memo.html'    
    
    def get_queryset(self): 
        index = self.kwargs['index']
        contents = FContent.objects.filter(forum_id=index).order_by("-id")
        return contents
    
    def get_context_data(self, **kwargs):
      index = self.kwargs['index']
      classroom_id = self.kwargs['classroom_id']
      user_id = self.request.user.id
      action = self.kwargs['action']
      context = super(ForumMemo, self).get_context_data(**kwargs)        
      enrolls = Enroll.objects.filter(classroom_id=classroom_id)
      datas = []
      fwork = FWork.objects.get(id=index)
      teacher_id = fwork.teacher_id
      subject = fwork.title
      if action == "2":
      	works_pool = SFWork.objects.filter(index=index, score=5).order_by("-id")
      else:
        # 一次取得所有 SFWork	
        works_pool = SFWork.objects.filter(index=index).order_by("-id", "publish")
      reply_pool = SFReply.objects.filter(index=index).order_by("-id")	
      file_pool = SFContent.objects.filter(index=index, visible=True).order_by("-id")	
      for enroll in enrolls:
      	works = list(filter(lambda w: w.student_id==enroll.student_id, works_pool))
      	# 對未作答學生不特別處理，因為 filter 會傳回 []
      	if len(works)>0:
      	  replys = list(filter(lambda w: w.work_id==works[-1].id, reply_pool))
      	  files = list(filter(lambda w: w.student_id==enroll.student_id, file_pool))
      	  if action == 2 :
            if works[-1].score == 5:
      	      datas.append([enroll, works, replys, files])
      	  else :
      	    datas.append([enroll, works, replys, files])
      	else :
      	  replys = []
      	  if not action == 2 :
            files = list(filter(lambda w: w.student_id==enroll.student_id, file_pool))
            datas.append([enroll, works, replys, files])
            
      def getKey(custom):
        if custom[1]:
          if action == 3:
            return custom[1][-1].like_count, -custom[0].seat
          elif action == 2:
            return custom[1][-1].score, custom[1][0].publication_date
          elif action == 1:
             return -custom[0].seat
          else :
             return custom[1][0].reply_date, -custom[0].seat
        else:
          if action == 3:
            return 0, -custom[0].seat
          elif action == 2:
            return 0, timezone.now()
          elif action == 1:
             return -custom[0].seat
          else :
             return datetime(2000, 1, 1, tzinfo=timezone.utc), -custom[0].seat
      datas = sorted(datas, key=getKey, reverse=True)	            
      context['action'] = action
      context['replys'] = replys
      context['datas'] = datas
      context['teacher_id'] = teacher_id
      context['subject'] = subject
      context['classroom_id'] = classroom_id
      context['index'] = index
      context['is_teacher'] = is_teacher(self.request.user, classroom_id)
      return context

class ForumHistory(ClassmateRequiredMixin, generic.ListView):
    model = SFWork
    template_name = 'student/forum_hitory.html'
       
    def get_context_data(self, **kwargs):
        context = super(ForumHistory, self).get_context_data(**kwargs)
        index = self.kwargs['index']
        classroom_id = self.kwargs['classroom_id']
        user_id = self.kwargs['user_id']
        work = []
        contents = FContent.objects.filter(forum_id=index).order_by("-id")
        works = SFWork.objects.filter(index=index, student_id=user_id).order_by("-id")
        files = SFContent.objects.filter(index=index, student_id=user_id).order_by("-id")
        forum = FWork.objects.get(id=index)
        context['forum'] = forum
        context['classroom_id'] = classroom_id
        context['works'] = works
        context['contents'] = contents
        context['files'] = files
        context['index'] = index
        if len(works)> 0 :
            if works[0].publish or user_id==str(request.user.id) or is_teacher(classroom_id, self.request.user.id):
              return context
        return redirect("/")
	
def forum_like(request):
    forum_id = request.POST.get('forumid')  
    classroom_id = request.POST.get('classroomid')  		
    user_id = request.POST.get('userid')
    action = request.POST.get('action')
    likes = []
    sfworks = []
    fwork = FWork.objects.get(id=forum_id)
    user = User.objects.get(id=user_id)
    if forum_id:
        try:
            sfworks = SFWork.objects.filter(index=forum_id, student_id=user_id)
            sfwork = sfworks[0]
            jsonDec = json.decoder.JSONDecoder()
            if action == "like":
                if sfwork.likes:
                    likes = jsonDec.decode(sfwork.likes)                     
                    if not request.user.id in likes:
                        likes.append(request.user.id)
                else:
                    likes.append(request.user.id)
                sfwork.likes = json.dumps(likes)
                sfwork.like_count = len(likes)								
                sfwork.save()
                update_avatar(request.user.id, 5, 0.1)
                # History
                history = PointHistory(user_id=request.user.id, kind=5, message=u'+0.1分--討論區按讚<'+fwork.title+'><'+user.first_name+'>', url="/student/forum/memo/"+classroom_id+"/"+forum_id+"/0/#"+user_id)
                history.save()										
            else:
                if sfwork.likes:
                    likes = jsonDec.decode(sfwork.likes)
                    if request.user.id in likes:
                        likes.remove(request.user.id)
                        sfwork.likes = json.dumps(likes)
                        sfwork.like_count = len(likes)
                        sfwork.save()
                        #積分 
                        update_avatar(request.user.id, 5, -0.1)
                        # History
                        history = PointHistory(user_id=request.user.id, kind=5, message=u'-0.1分--討論區按讚取消<'+fwork.title+'><'+user.first_name+'>', url="/student/forum/memo/"+classroom_id+"/"+forum_id+"/0/#"+user_id)
                        history.save()		               
        except ObjectDoesNotExist:
            sfworks = []            
        
        return JsonResponse({'status':'ok', 'likes':sfworks[0].likes}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        

def forum_reply(request):
    forum_id = request.POST.get('forumid')  
    classroom_id = request.POST.get('classroomid')		
    user_id = request.POST.get('userid')
    work_id = request.POST.get('workid')		
    text = request.POST.get('reply')
    fwork = FWork.objects.get(id=forum_id)
    user = User.objects.get(id=user_id)
    if forum_id:       
        reply = SFReply(index=forum_id, work_id=work_id, user_id=user_id, memo=text, publication_date=timezone.now())
        reply.save()
        sfwork = SFWork.objects.get(id=work_id)
        sfwork.reply_date = timezone.now()
        sfwork.save()
        update_avatar(request.user.id, 6, 0.2)
        # History
        history = PointHistory(user_id=request.user.id, kind=6, message=u'0.2分--討論區留言<'+fwork.title+'><'+user.first_name+'>', url='/student/forum/memo/'+classroom_id+'/'+forum_id+'/0/#'+user_id)
        history.save()		              
				
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        

			
def forum_guestbook(request):
    work_id = request.POST.get('workid')  
    guestbooks = "<table class=table>"
    if work_id:
        try :
            replys = SFReply.objects.filter(work_id=work_id).order_by("-id")
        except ObjectDoesNotExist:
            replys = []
        for reply in replys:
            user = User.objects.get(id=reply.user_id)
            guestbooks += '<tr><td nowrap>' + user.first_name + '</td><td>' + reply.memo + "</td></tr>"
        guestbooks += '</table>'
        return JsonResponse({'status':'ok', 'replys': guestbooks}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        
			
def forum_people(request):
    forum_id = request.POST.get('forumid')  
    user_id = request.POST.get('userid')
    likes = []
    sfworks = []
    names = []
    if forum_id:
        try:
            sfworks = SFWork.objects.filter(index=forum_id, student_id=user_id).order_by("id")
            sfwork = sfworks[0]
            jsonDec = json.decoder.JSONDecoder()
            if sfwork.likes:
                likes = jsonDec.decode(sfwork.likes)  
                for like in reversed(likes):
                  user = User.objects.get(id=like)
                  names.append('<button type="button" class="btn btn-default">'+user.first_name+'</button>')
        except ObjectDoesNotExist:
            sfworks = []                   
        return JsonResponse({'status':'ok', 'likes':names}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        

def forum_score(request):
    work_id = request.POST.get('workid')  
    classroom_id = request.POST.get('classroomid')  
    user_id = request.POST.get('userid')  		
    score = request.POST.get('score')
    comment = request.POST.get('comment')		
    if work_id and is_teacher(request.user, classroom_id):
        sfwork = SFWork.objects.get(id=work_id)
        sfwork.score = score
        sfwork.comment = comment
        sfwork.scorer = request.user.id
        sfwork.comment_publication_date = timezone.now()
        sfwork.save()
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        

# 統計某討論主題所有同學心得
class ForumJieba(ClassmateRequiredMixin, ListView):
    model = SFWork
    context_object_name = 'contents'
    template_name = 'student/forum_jieba.html'    
    
    def get_context_data(self, **kwargs):
      context = super(ForumJieba, self).get_context_data(**kwargs)      
      index = self.kwargs['index']
      classroom_id = self.kwargs['classroom_id']
      classroom = Classroom.objects.get(id=classroom_id)
      enrolls = Enroll.objects.filter(classroom_id=classroom_id)
      works = []
      contents = FContent.objects.filter(forum_id=index).order_by("-id")
      fwork = FWork.objects.get(id=index)
      teacher_id = fwork.teacher_id
      subject = fwork.title
      memo = ""
      for enroll in enrolls:
        try:
            works = SFWork.objects.filter(index=index, student_id=enroll.student_id).order_by("-id")
            if works:
                memo += works[0].memo
        except ObjectDoesNotExist:
            pass
      memo = memo.rstrip('\r\n')
      seglist = jieba.cut(memo, cut_all=False)
      hash = {}
      for item in seglist: 
        if item in hash:
            hash[item] += 1
        else:
            hash[item] = 1
      words = []
      count = 0
      error=""
      for key, value in sorted(hash.items(), key=lambda x: x[1], reverse=True):
        if ord(key[0]) > 32 :
            count += 1	
            words.append([key, value])
            if count == 100:
                break
      context['index'] = index
      context['words'] = words
      context['enrolls'] = enrolls
      context['classroom'] = classroom
      context['subject'] = subject
      return context

# 統計某討論主題所有同學心得
class ForumWord(ClassmateRequiredMixin, ListView):
    model = SFWork
    context_object_name = 'contents'
    template_name = 'student/forum_word.html'    
    
    def get_context_data(self, **kwargs):
        context = super(ForumWord, self).get_context_data(**kwargs)      
        index = self.kwargs['index']
        classroom_id = self.kwargs['classroom_id']
        word = self.kwargs['word']        
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        work_ids = []
        datas = []
        pos = word.index(' ')
        word = word[0:pos]
        for enroll in enrolls:
            try:
                works = SFWork.objects.filter(index=index, student_id=enroll.student_id,memo__contains=word).order_by("-id")
                if works:
                    work_ids.append(works[0].id)
                    datas.append([works[0], enroll.seat])
            except ObjectDoesNotExist:
                pass
        classroom = Classroom.objects.get(id=classroom_id)
        for work, seat in datas:
            work.memo = work.memo.replace(word, '<font color=red>'+word+'</font>')
        context['word'] = word
        context['datas'] = datas
        context['classroom'] = classroom
        return context
		
# 下載檔案
def forum_download(request, file_id):
    content = SFContent.objects.get(id=file_id)
    filename = content.title	
    download =  settings.BASE_DIR + "/static/upload/" + content.filename
    wrapper = FileWrapper(open( download, "rb" ))
    response = HttpResponse(wrapper, content_type = 'application/force-download')
    filename_header = filename_browser(filename)
    response['Content-Disposition'] = 'attachment; ' + filename_header
    return response
	
# 顯示圖片
def forum_showpic(request, file_id):
        content = SFContent.objects.get(id=file_id)
        return render(request, 'student/forum_showpic.html', {'content':content})

# ajax刪除檔案
def forum_file_delete(request):
    file_id = request.POST.get('fileid')  
    if file_id:
        try:
            file = SFContent.objects.get(id=file_id)
            file.visible = False
            file.delete_date = timezone.now()
            file.save()
        except ObjectDoesNotExist:
            file = []           
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)        					
		
def show(request, typing, lesson, index, user_id):
    classmate=False
    profile = Profile.objects.get(user=user_id)
    jsonDec = json.decoder.JSONDecoder()		
    if len(profile.classroom) > 0 :		
        classroom_list = jsonDec.decode(profile.classroom)
        for classroom in classroom_list:
            if is_classmate(request.user, classroom):
                classmate = True
                break
    if not classmate:
	    return redirect("/")
    work_dict = dict(((work.index, [work, WorkFile.objects.filter(work_id=work.id).order_by("-id")]) for work in Work.objects.filter(typing=typing, lesson=lesson, user_id=request.user.id)))
    if user_id == request.user.id or request.user.is_superuser:
        try:
            work = Work.objects.get(typing=typing, lesson=lesson, index=index, user_id=user_id)
        except ObjectDoesNotExist:
            work = None
        except MultipleObjectsReturned:
            work = Work.objects.filter(typing=typing, lesson=lesson, index=index, user_id=user_id).last()
        return render(request, 'student/show.html', {'work':work, 'lesson':lesson, 'work_dict':work_dict, 'index':index})
    else :
        return redirect("/")

def survey(request, classroom_id):
    return render(request, 'student/survey.html', {'classroom_id':classroom_id})
	
# 列出所有討論測驗
class ExamListView(ClassmateRequiredMixin, ListView):
    model = Exam
    context_object_name = 'exams'
    template_name = 'student/exam_list.html'    
    
    def get_queryset(self):
        queryset = []
        examclass_dict = dict(((examclass.exam_id, examclass) for examclass in ExamClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))	
        #fclasses = FClass.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        exams = Exam.objects.filter(id__in=examclass_dict.keys()).order_by("-id")
        examwork_pool = ExamWork.objects.filter(student_id=self.request.user.id).order_by("-id")
        for exam in exams:
            questions = ExamQuestion.objects.filter(exam_id=exam.id)					
            examworks = list(filter(lambda w: w.exam_id==exam.id, examwork_pool))
            retest = False
            examclass = examclass_dict[exam.id]
            if len(examworks) < examclass.round_limit or examclass.round_limit == 0 :
                retest = True
            if len(examworks)> 0 :
                queryset.append([exam, examworks[0].publish, examclass_dict[exam.id], examworks, len(questions), examclass_dict[exam.id], retest])
            else :
                queryset.append([exam, False, examclass_dict[exam.id], 0, len(questions), examclass_dict[exam.id], retest])
        def getKey(custom):
            return custom[2].publication_date, custom[2].exam_id
        queryset = sorted(queryset, key=getKey, reverse=True)	
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(ExamListView, self).get_context_data(**kwargs)
        context['classroom_id'] = self.kwargs['classroom_id']
        context['examclasses'] = dict(((examclass.exam_id, examclass) for examclass in ExamClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))
        return context	    

    # 限本班同學
    def render(request,self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        return super(ExamListView, self).render(request,context)    	
			
def exam_question(request, classroom_id, exam_id, examwork_id, question_id):
    if not is_classmate(request.user, classroom_id):
        return redirect("/")	
    exam = Exam.objects.get(id=exam_id)
    examworks = ExamWork.objects.filter(exam_id=exam_id, student_id=request.user.id).order_by("-id")

    if len(examworks)> 0:
        if examworks[0].publish:
            questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("?")
            question_ids = []		
            for question in questions:
                question_ids.append(question.id)
            question_string = ",".join(str(question_id) for question_id in question_ids)			
            examwork = ExamWork(exam_id=exam_id, student_id=request.user.id, questions=question_string)
        else :
            examwork = examworks[0]
    else :
        questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("?")
        question_ids = []		
        for question in questions:
            question_ids.append(question.id)
        question_string = ",".join(str(question_id) for question_id in question_ids)			
        examwork = ExamWork(exam_id=exam_id, student_id=request.user.id, questions=question_string)
    examwork.save()
    questions = examwork.questions
    question_ids = questions.split(',')
    qas = []
    answer_dict = dict(((answer.question_id, answer) for answer in ExamAnswer.objects.filter(examwork_id=examwork.id, question_id__in=question_ids, student_id=request.user.id))) 
    for question in question_ids:
        question = int(question)
        if question in answer_dict:
            qas.append([question, answer_dict[question]])
        else :
            qas.append([question, 0])
    if not question_id == 0:
        question = ExamQuestion.objects.get(id=question_id)
    else :
        if len(questions)> 0 :
            return redirect('/student/exam/question/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/'+str(question_ids[0]))
        else :
            return redirect('/student/exam/'+str(classroom_id))
    try :
        answer = ExamAnswer.objects.get(examwork_id=examwork.id, question_id=question_id, student_id=request.user.id).answer
    except ObjectDoesNotExist:
        answer = 0
    return render(request,'student/exam_question.html', {'examwork': examwork, 'answer':answer, 'exam':exam, 'qas':qas, 'question':question, 'question_id':question_id, 'classroom_id': classroom_id})
			
# Ajax 設定測驗答案
def exam_answer(request):
    examwork_id = request.POST.get('examworkid')	
    question_id = request.POST.get('questionid')
    input_answer = request.POST.get('answer')
    if examwork_id :
        try:
            examwork = ExamWork.objects.get(id=examwork_id)
        except ObjectDoesNotExist:
	         examwork = ExamWork(exam_id=exam_id, student_id=request.user.id)
        if not examwork.publish :
            try :
               answer = ExamAnswer.objects.get(examwork_id=examwork_id, question_id=question_id, student_id=request.user.id) 	
            except ObjectDoesNotExist :
                answer = ExamAnswer(examwork_id=examwork_id, question_id=question_id, student_id=request.user.id)
            answer.answer = input_answer
            answer.save()
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)
	
def exam_submit(request, classroom_id, exam_id, examwork_id):
    if not is_classmate(request.user, classroom_id):
        return redirect("/")
    examclass = ExamClass.objects.get(exam_id=exam_id, classroom_id=classroom_id)
    examworks = ExamWork.objects.filter(exam_id=exam_id, student_id=request.user.id)
    if examclass.round_limit == 0 or len(examworks) <= examclass.round_limit:
        try:
            examwork = ExamWork.objects.get(id=examwork_id)
        except ObjectDoesNotExist:
	          examwork = ExamWork(exam_id=exam_id, student_id=request.user.id)	
        examwork.publish = True
        examwork.publication_date = timezone.now()
        questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("id")	
        question_ids = []
        score = 0
        for question in questions:
            question_ids.append(question.id)		
        answer_dict = dict(((answer.question_id, answer.answer) for answer in ExamAnswer.objects.filter(examwork_id=examwork_id, question_id__in=question_ids, student_id=request.user.id)))		
        for question in questions:
            if question.id in answer_dict:
                if question.answer == answer_dict[question.id] :
                    score += question.score		
        examwork.score = score
        examwork.scorer = 0
        examwork.save()
    return redirect('/student/exam/score/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/0')

def exam_score(request, classroom_id, exam_id, examwork_id, question_id):
    if not is_classmate(request.user, classroom_id):
        return redirect("/")
    score = 0
    score_total = 0
    exam = Exam.objects.get(id=exam_id)
    try:
        examwork = ExamWork.objects.get(id=examwork_id)
    except ObjectDoesNotExist:
        pass
    question_ids = examwork.questions.split(',')
    score_answer = dict(((question.id, [question.score, question.answer]) for question in ExamQuestion.objects.filter(exam_id=exam_id)))			
    qas = []
    for question in question_ids:
        score_total += score_answer[int(question)][0]
    answer_dict = dict(((answer.question_id, answer.answer) for answer in ExamAnswer.objects.filter(examwork_id=examwork_id, question_id__in=question_ids, student_id=request.user.id)))		
    for question in question_ids:
        question = int(question)
        if question in answer_dict:
            if score_answer[question][1] == answer_dict[question] :
                score += score_answer[question][0]
            qas.append([question, score_answer[question][1], answer_dict[question]])
        else :
            qas.append([question, score_answer[question][1], 0])
    if not question_id == 0:
        question = ExamQuestion.objects.get(id=question_id)
    else :
        return redirect('/student/exam/score/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/'+str(question_ids[0]))
    try :
        answer = ExamAnswer.objects.get(examwork_id=examwork_id, question_id=question_id, student_id=request.user.id).answer
    except ObjectDoesNotExist:
        answer = 0

    return render(request,'student/exam_score.html', {'examwork': examwork, 'score_total': score_total, 'score':score, 'question':question, 'answer':answer, 'exam':exam, 'qas':qas})
			
# 列出組別
class GroupListView(ListView):
    model = ClassroomGroup
    context_object_name = 'groups'
    paginate_by = 30
    template_name = 'student/group.html'
    
    def get_queryset(self):
        queryset = ClassroomGroup.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        return queryset         			

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)        
        context['classroom_id'] = self.kwargs['classroom_id']
        return context	    			

# 顯示所有組別
def group_list(request, group_id):
        groups = []
        student_groups = {}
        enroll_list = []
        group_list = {}
        group_ids = []
        group = ClassroomGroup.objects.get(id=group_id)
        numbers = group.numbers
        enrolls = Enroll.objects.filter(classroom_id=group.classroom_id).order_by("seat")
        for enroll in enrolls:
            enroll_list.append(enroll.id)
        enroll_groups = StudentGroup.objects.filter(enroll_id__in=enroll_list, group_id=group_id)
        for enroll_group in enroll_groups:
            if enroll_group.group > -1:
                group_ids.append(enroll_group.enroll_id)
                group_list[enroll_group.enroll_id] = enroll_group.group
                enroll = Enroll.objects.get(id=enroll_group.enroll_id)
                if enroll_group.group in student_groups :
                    student_groups[enroll_group.group].append(enroll)
                else:
                    student_groups[enroll_group.group]=[enroll]	            
        for i in range(numbers):
            try: 
                leader_id = StudentGroupLeader.objects.get(group_id=group_id, group=i).enroll_id
                leader = Enroll.objects.get(id=leader_id)
            except ObjectDoesNotExist:
                leader_id = 0
                leader = None
            if i in student_groups:
                groups.append([i, student_groups[i], leader])
            else:
                groups.append([i, [], leader])
					
        #找出尚未分組的學生
        no_group = []
        for enroll in enrolls:
            if not enroll.id in group_ids:
                no_group.append([enroll.seat, enroll.student])
    
        enroll_user = Enroll.objects.get(student_id=request.user.id, classroom_id=group.classroom_id)
        try:
            user_group = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll_user.id).group
        except ObjectDoesNotExist:
            user_group = -1
        return render(request,'student/group_join.html', {'user_group':user_group, 'group':group, 'groups':groups, 'enroll_id':enroll_user.id, 'student_groups':student_groups, 'no_group':no_group, 'classroom_id':group.classroom_id, 'group_id':group_id})

			
# 顯示所有組別
def group_join(request, group_id, number, enroll_id):
    try:
        group = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll_id)
        group.group = number
    except ObjectDoesNotExist:
        group = StudentGroup(group_id=group_id, enroll_id=enroll_id, group=number)
    if ClassroomGroup.objects.get(id=group_id).opening:
        group.save()
    StudentGroupLeader.objects.filter(group_id=group_id, enroll_id=enroll_id).delete()
			
    return redirect("/student/group/list/"+str(group_id))

# 設為組長
def group_leader(request, group_id, number, enroll_id):
    try:
        group = StudentGroupLeader.objects.get(group_id=group_id, group=number)
        group.enroll_id = enroll_id
    except ObjectDoesNotExist:
        group = StudentGroupLeader(group_id=group_id, enroll_id=enroll_id, group=number)
    if ClassroomGroup.objects.get(id=group_id).opening:
        group.save()			
			
    return redirect("/student/group/list/"+str(group_id))
# 各種課程
def lessons1(request, subject_id):
    hit = statics_lesson(request, subject_id)
    if request.user.is_authenticated():
        user_id = request.user.id
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)
        if subject_id == "A":
            lock = profile.lock1
        else:
            lock = profile.lock1
    else :
        user_id = 0
        lock = 1
    return render(request, 'student/lessons1.html', {'subject_id': subject_id, 'counter': hit, 'lock':lock})

def statics_lesson(request, lesson):
    try :
        counter = LessonCounter.objects.get(name=lesson)
        counter.hit = counter.hit + 1
    except ObjectDoesNotExist:
        counter = LessonCounter(name=lesson, hit=1)
    except MultipleObjectsReturned:
        counters = LessonCounter.objects.filter(name=lesson)
        counter = counter[0]
        counter.hit = counter.hit + 1
    counter.save()
    day = str(datetime.now())[0:4]+str(datetime.now())[5:7]+str(datetime.now())[8:10]
    try :
        daycounter = DayCounter.objects.get(day=day)
        daycounter.hit = daycounter.hit + 1
    except ObjectDoesNotExist:
        daycounter = DayCounter(day=day, hit=1)
    except MultipleObjectsReturned:
        daycounters = DayCounter.objects.filter(day=day)
        daycounter = daycounters[0]
        daycounter.hit = daycounter.hit + 1
    daycounter.save()
    log = LogCounter(counter_id=counter.id, counter_ip=request.META['REMOTE_ADDR'])
    log.save()
    return counter.hit


# 課程內容
def lesson1(request, lesson):
    work_dict = {}
    hit = statics_lesson(request, lesson)

    if request.user.id > 0 :
        profile = Profile.objects.get(user=request.user)
    else:
        profile = Profile()
    if lesson[0] == "A":
        lesson_id = 1
        profile_lock = profile.lock1
        work_dict = dict(((work.index, [work, WorkFile.objects.filter(work_id=work.id).order_by("-id")]) for work in Work.objects.filter(typing=0, lesson=lesson_id, user_id=request.user.id)))
        # 限登入者
        if not request.user.id > 0:
            return redirect("/account/login/0")
        else :
            lock = {'A002':2, 'A003':3, 'A004':5, 'A005':7, 'A006':9, 'A007':11, 'A008':13, 'A009':14, 'A010':15, 'A011':16}
        if lesson in lock:
            if profile_lock < lock[lesson]:
                if not request.user.groups.filter(name='teacher').exists():
                    return redirect("/")
        return render(request, 'student/lessonA.html', {'lesson': lesson, 'lesson_id': lesson_id, 'work_dict': work_dict, 'counter':hit, 'typing':"0" })
    else:
        lesson_id = 1
        profile_lock = profile.lock1
        work_dict = dict(((work.index, [work, WorkFile.objects.filter(work_id=work.id).order_by("-id")]) for work in Work.objects.filter(typing=0, lesson=lesson_id, user_id=request.user.id)))
        return render(request, 'student/lessonA.html', {'lesson': lesson, 'lesson_id': lesson_id, 'work_dict': work_dict, 'counter':hit, 'typing':"0"})

'''
--------------------思辨區
'''
# 列出所有討論主題
class SpeculationListView(ListView):
    model = SSpeculationWork
    context_object_name = 'works'
    template_name = 'student/speculation_list.html'    
    
    def get_queryset(self):
        queryset = []
        fclass_dict = dict(((fclass.forum_id, fclass) for fclass in SpeculationClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))	
        #fclasses = FClass.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        fworks = SpeculationWork.objects.filter(id__in=fclass_dict.keys()).order_by("-id")
        sfwork_pool = SSpeculationWork.objects.filter(student_id=self.request.user.id).order_by("-id")
        for fwork in fworks:
            sfworks = filter(lambda w: w.index==fwork.id, sfwork_pool)
            if len(sfworks)> 0 :
                queryset.append([fwork, sfworks[0].publish, fclass_dict[fwork.id], len(sfworks)])
            else :
                queryset.append([fwork, False, fclass_dict[fwork.id], 0])
        def getKey(custom):
            return custom[2].publication_date, custom[2].forum_id
        queryset = sorted(queryset, key=getKey, reverse=True)	
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(SpeculationListView, self).get_context_data(**kwargs)
        context['classroom_id'] = self.kwargs['classroom_id']
        context['bookmark'] =  self.kwargs['bookmark']
        context['fclasses'] = dict(((fclass.forum_id, fclass) for fclass in FClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))
        return context	    

    # 限本班同學
    def render(request,self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        return super(SpeculationListView, self).render(request,context)    


def speculation_submit(request, classroom_id, index):
        scores = []
        works = SSpeculationWork.objects.filter(index=index, student_id=request.user.id).order_by("-id")
        contents = SpeculationContent.objects.filter(forum_id=index)
        fwork = SpeculationWork.objects.get(id=index)
        types = SpeculationAnnotation.objects.filter(forum_id=index)
        if request.method == 'POST':
            form = SpeculationSubmitForm(request.POST, request.FILES)
            #第一次上傳加上積分
            works = SSpeculationWork.objects.filter(index=index, student_id=request.user.id).order_by("-id")
            publish = False
            work = SSpeculationWork(index=index, student_id=request.user.id, publish=publish)
            work.save()
            if request.FILES:
                content = SSpeculationContent(index=index, student_id=request.user.id)
                myfile =  request.FILES.get("file", "")
                fs = FileSystemStorage()
                filename = uuid4().hex
                content.title = myfile.name
                content.work_id = work.id
                content.filename = str(request.user.id)+"/"+filename
                fs.save("static/upload/"+str(request.user.id)+"/"+filename, myfile)
                content.save()
            if form.is_valid():
                work.memo=form.cleaned_data['memo']
                work.save()
                if not works:
                    return redirect("/student/speculation/publish/"+classroom_id+"/"+index+"/2")	
                elif not works[0].publish:
                    return redirect("/student/speculation/publish/"+classroom_id+"/"+index+"/2")
                return redirect("/student/speculation/annotate/"+classroom_id+"/"+index+"/"+str(request.user.id))
            else:
                return render(request,'student/speculation_form.html', {'error':form.errors})
        else:
            if not works.exists():
                work = SSpeculationWork(index=0, publish=False)
                form = SpeculationSubmitForm()
            else:
                work = works[0]
                form = SpeculationSubmitForm()
            files = SSpeculationContent.objects.filter(index=index, student_id=request.user.id,visible=True).order_by("-id")
            subject = SpeculationWork.objects.get(id=index).title
        return render(request,'student/speculation_form.html', {'classroom_id':classroom_id, 'subject':subject, 'files':files, 'index': index, 'fwork':fwork, 'works':works, 'work':work, 'form':form, 'scores':scores, 'index':index, 'contents':contents, 'types': types})

# 發表心得
def speculation_publish(request, classroom_id, index, action):
    if action == "1":
        try:
            works = SSpeculationWork.objects.filter(index=index, student_id=request.user.id).order_by("-id")
            work = works[0]
            work.publish = True
            work.save()
            update_avatar(request.user.id, 1, 2)
            # History
            fwork = FWork.objects.get(id=index)
            history = PointHistory(user_id=request.user.id, kind=1, message=u'2分--繳交思辨區作業<'+fwork.title+'>', url='/student/speculation/annotate/'+classroom_id+'/'+index+'/'+str(request.user.id))
            history.save()							
        except ObjectDoesNotExist:
            pass
        return redirect("/student/speculation/annotate/"+classroom_id+"/"+index+"/"+str(request.user.id))
    elif action == "0":
        return redirect("/student/speculation/annotate/"+classroom_id+"/"+index+"/"+str(request.user.id))
    else :
        return render(request,'student/speculation_publish.html', {'classroom_id': classroom_id, 'index': index})
	
			
# 列出班級思辨
class SpeculationAnnotateView(ListView):
    model = SSpeculationWork
    context_object_name = 'works'
    template_name = 'student/speculation_annotate.html'    
    
    def get_queryset(self):
        works = SSpeculationWork.objects.filter(index=self.kwargs['index'], student_id=self.kwargs['id']).order_by("-id")          	
        works = list(works)
        return works
        
    def get_context_data(self, **kwargs):
        context = super(SpeculationAnnotateView, self).get_context_data(**kwargs)        
        ids = []
        queryset = []
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("seat")
        for enroll in enrolls :
            ids.append(enroll.student_id)
        work_pool = SSpeculationWork.objects.filter(index=self.kwargs['index'], student_id__in=ids).order_by("-id")
        for enroll in enrolls:
            works = filter(lambda w: w.student_id==enroll.student_id, work_pool)
            if len(works)> 0:
                queryset.append([enroll, works[0].publish])
            else:
                queryset.append([enroll, False])
        context['queryset'] = queryset
        context['classroom_id'] = self.kwargs['classroom_id']
        context['student_id'] = int(self.kwargs['id'])
        context['enrolls'] = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("seat")
        context['swork'] = SpeculationWork.objects.get(id=self.kwargs['index'])
        context['contents'] = SpeculationContent.objects.filter(forum_id=self.kwargs['index'])
        context['files'] = SSpeculationContent.objects.filter(index=self.kwargs['index'], student_id=self.kwargs['id'])
        context['types'] = SpeculationAnnotation.objects.filter(forum_id=self.kwargs['index'])
        context['index'] = self.kwargs['index']
        return context

    # 限本班同學
    def render(request,self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        return super(SpeculationAnnotateView, self).render(request,context)    

# 列出班級思辨
class SpeculationAnnotateClassView(ListView):
    model = SSpeculationWork
    context_object_name = 'annotations'
    template_name = 'student/speculation_annotate_class.html'    
    
    def get_queryset(self):
        annotations = SpeculationAnnotation.objects.filter(forum_id=self.kwargs['index'])
        return annotations
        
    def get_context_data(self, **kwargs):
        context = super(SpeculationAnnotateClassView, self).get_context_data(**kwargs)        
        context['classroom_id'] = self.kwargs['classroom_id']
        context['annotate_id'] = int(self.kwargs['id'])
        context['enrolls'] = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id'])
        context['swork'] = SpeculationWork.objects.get(id=self.kwargs['index'])
        context['contents'] = SpeculationContent.objects.filter(forum_id=self.kwargs['index'])
        context['types'] = SpeculationAnnotation.objects.filter(forum_id=self.kwargs['index'])
        context['index'] = self.kwargs['index']
        return context	    

    # 限本班同學
    def render(request,self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        if self.kwargs['id'] == "0":
            annotations = SpeculationAnnotation.objects.filter(forum_id=self.kwargs['index'])
            if len(annotations)>0:
                return redirect("/student/speculation/annotateclass/"+self.kwargs['classroom_id']+"/"+self.kwargs['index']+"/"+str(annotations[0].id))
        return super(SpeculationAnnotateClassView, self).render(request,context)    

			
# 下載檔案
def speculation_download(request, file_id):
    content = SSpeculationContent.objects.get(id=file_id)
    filename = content.title
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))		
    download =  BASE_DIR + "/static/upload/" + content.filename
    wrapper = FileWrapper(file( download, "r" ))
    response = HttpResponse(wrapper, content_type = 'application/force-download')
    #response = HttpResponse(content_type='application/force-download')
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename.encode('utf8'))
    # It's usually a good idea to set the 'Content-Length' header too.
    # You can also set any other required headers: Cache-Control, etc.
    return response
	
# 顯示圖片
def speculation_showpic(request, file_id):
        content = SSpeculationContent.objects.get(id=file_id)
        return render(request,'student/forum_showpic.html', {'content':content})

# 列出組別
class GroupListView(ListView):
    model = ClassroomGroup
    context_object_name = 'groups'
    paginate_by = 30
    template_name = 'student/group.html'
    
    def get_queryset(self):
        queryset = ClassroomGroup.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        return queryset         			

    def get_context_data(self, **kwargs):
        context = super(GroupListView, self).get_context_data(**kwargs)        
        context['classroom_id'] = self.kwargs['classroom_id']
        return context	    			

def speculation_score(request):
    work_id = request.POST.get('workid')  
    classroom_id = request.POST.get('classroomid')  
    user_id = request.POST.get('userid')  		
    score = request.POST.get('score')
    comment = request.POST.get('comment')		
    if work_id and is_teacher(classroom_id, request.user.id):
        sfwork = SSpeculationWork.objects.get(id=work_id)
        sfwork.score = score
        sfwork.comment = comment
        sfwork.scorer = request.user.id
        sfwork.comment_publication_date = timezone.now()
        sfwork.save()
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':1}, safe=False)        

		
# 顯示所有組別
def group_list(request, group_id):
        groups = []
        student_groups = {}
        enroll_list = []
        group_list = {}
        group_ids = []
        group = ClassroomGroup.objects.get(id=group_id)
        numbers = group.numbers
        enrolls = Enroll.objects.filter(classroom_id=group.classroom_id).order_by("seat")
        for enroll in enrolls:
            enroll_list.append(enroll.id)
        enroll_groups = StudentGroup.objects.filter(enroll_id__in=enroll_list, group_id=group_id)
        for enroll_group in enroll_groups:
            group_ids.append(enroll_group.enroll_id)
            group_list[enroll_group.enroll_id] = enroll_group.group
            enroll = Enroll.objects.get(id=enroll_group.enroll_id)
            if enroll_group.group in student_groups:
                student_groups[enroll_group.group].append(enroll)
            else:
                student_groups[enroll_group.group]=[enroll]	            
        for i in range(numbers):
            try: 
                leader_id = StudentGroupLeader.objects.get(group_id=group_id, group=i).enroll_id
                leader = Enroll.objects.get(id=leader_id)
            except ObjectDoesNotExist:
                leader_id = 0
                leader = None
            if i in student_groups:
                groups.append([i, student_groups[i], leader])
            else:
                groups.append([i, [], leader])
					
        #找出尚未分組的學生
        no_group = []
        for enroll in enrolls:
            if not enroll.id in group_ids:
                no_group.append([enroll.seat, enroll.student])
    
        enroll_user = Enroll.objects.get(student_id=request.user.id, classroom_id=group.classroom_id)
        try:
            user_group = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll_user.id).group
        except ObjectDoesNotExist:
            user_group = -1
        return render(request,'student/group_join.html', {'user_group':user_group, 'group':group, 'groups':groups, 'enroll_id':enroll_user.id, 'student_groups':student_groups, 'no_group':no_group, 'classroom_id':group.classroom_id, 'group_id':group_id})

			
# 顯示所有組別
def group_join(request, group_id, number, enroll_id):
    try:
        group = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll_id)
        group.group = number
    except ObjectDoesNotExist:
        group = StudentGroup(group_id=group_id, enroll_id=enroll_id, group=number)
    if ClassroomGroup.objects.get(id=group_id).opening:
        group.save()
    StudentGroupLeader.objects.filter(group_id=group_id, enroll_id=enroll_id).delete()
			
    return redirect("/student/group/list/"+str(group_id))

# 設為組長
def group_leader(request, group_id, number, enroll_id):
    try:
        group = StudentGroupLeader.objects.get(group_id=group_id, group=number)
        group.enroll_id = enroll_id
    except ObjectDoesNotExist:
        group = StudentGroupLeader(group_id=group_id, enroll_id=enroll_id, group=number)
    if ClassroomGroup.objects.get(id=group_id).opening:
        group.save()			
			
    return redirect("/student/group/list/"+str(group_id))


# 列出所有討論測驗
class ExamListView(ListView):
    model = Exam
    context_object_name = 'exams'
    template_name = 'student/exam_list.html'    
    
    def get_queryset(self):
        queryset = []
        examclass_dict = dict(((examclass.exam_id, examclass) for examclass in ExamClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))	
        #fclasses = FClass.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by("-id")
        exams = Exam.objects.filter(id__in=examclass_dict.keys()).order_by("-id")
        examwork_pool = ExamWork.objects.filter(student_id=self.request.user.id).order_by("-id")
        for exam in exams:
            questions = ExamQuestion.objects.filter(exam_id=exam.id)					
            examworks = list(filter(lambda w: w.exam_id==exam.id, examwork_pool))
            retest = False
            examclass = examclass_dict[exam.id]
            if len(examworks) < examclass.round_limit or examclass.round_limit == 0 :
                retest = True
            if len(examworks)> 0 :
                queryset.append([exam, examworks[0].publish, examclass_dict[exam.id], examworks, len(questions), examclass_dict[exam.id], retest])
            else :
                queryset.append([exam, False, examclass_dict[exam.id], 0, len(questions), examclass_dict[exam.id], retest])
        def getKey(custom):
            return custom[2].publication_date, custom[2].exam_id
        queryset = sorted(queryset, key=getKey, reverse=True)	
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(ExamListView, self).get_context_data(**kwargs)
        context['classroom_id'] = self.kwargs['classroom_id']
        context['examclasses'] = dict(((examclass.exam_id, examclass) for examclass in ExamClass.objects.filter(classroom_id=self.kwargs['classroom_id'])))
        return context	    

    # 限本班同學
    def render(request,self, context):
        try:
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
        except ObjectDoesNotExist :
            return redirect('/')
        return super(ExamListView, self).render(request,context)    	
			
def exam_question(request, classroom_id, exam_id, examwork_id, question_id):	
    exam = Exam.objects.get(id=exam_id)
    examworks = ExamWork.objects.filter(exam_id=exam_id, student_id=request.user.id).order_by("-id")

    if len(examworks)> 0:
        if examworks[0].publish:
            questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("?")
            question_ids = []		
            for question in questions:
                question_ids.append(question.id)
            question_string = ",".join(str(question_id) for question_id in question_ids)			
            examwork = ExamWork(exam_id=exam_id, student_id=request.user.id, questions=question_string)
        else :
            examwork = examworks[0]
    else :
        questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("?")
        question_ids = []		
        for question in questions:
            question_ids.append(question.id)
        question_string = ",".join(str(question_id) for question_id in question_ids)			
        examwork = ExamWork(exam_id=exam_id, student_id=request.user.id, questions=question_string)
    examwork.save()
    questions = examwork.questions
    question_ids = questions.split(',')
    qas = []
    answer_dict = dict(((answer.question_id, answer) for answer in ExamAnswer.objects.filter(examwork_id=examwork.id, question_id__in=question_ids, student_id=request.user.id))) 
    for question in question_ids:
        question = int(question)
        if question in answer_dict:
            qas.append([question, answer_dict[question]])
        else :
            qas.append([question, 0])
    if not question_id == 0:
        question = ExamQuestion.objects.get(id=question_id)
    else :
        if len(questions)> 0 :
            return redirect('/student/exam/question/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/'+str(question_ids[0]))
        else :
            return redirect('/student/exam/'+str(classroom_id))
    try :
        answer = ExamAnswer.objects.get(examwork_id=examwork.id, question_id=question_id, student_id=request.user.id).answer
    except ObjectDoesNotExist:
        answer = ""
    return render(request,'student/exam_question.html', {'examwork': examwork, 'answer':answer, 'exam':exam, 'qas':qas, 'question':question, 'question_id':question_id, 'classroom_id': classroom_id})
			
# Ajax 設定測驗答案
def exam_answer(request):
    examwork_id = request.POST.get('examworkid')	
    question_id = request.POST.get('questionid')
    input_answer = request.POST.get('answer')
    if examwork_id :
        question = ExamQuestion.objects.get(id=question_id)
        try:
            examwork = ExamWork.objects.get(id=examwork_id)
        except ObjectDoesNotExist:
	         examwork = ExamWork(exam_id=exam_id, student_id=request.user.id)
        if not examwork.publish :
            try :
               answer = ExamAnswer.objects.get(examwork_id=examwork_id, question_id=question_id, student_id=request.user.id) 	
            except ObjectDoesNotExist :
                answer = ExamAnswer(examwork_id=examwork_id, question_id=question_id, student_id=request.user.id)
            answer.answer = input_answer
            answer.save()
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)
	
def exam_submit(request, classroom_id, exam_id, examwork_id):
    examclass = ExamClass.objects.get(exam_id=exam_id, classroom_id=classroom_id)
    examworks = ExamWork.objects.filter(exam_id=exam_id, student_id=request.user.id)
    if examclass.round_limit == 0 or len(examworks) <= examclass.round_limit:
        try:
            examwork = ExamWork.objects.get(id=examwork_id)
        except ObjectDoesNotExist:
	          examwork = ExamWork(exam_id=exam_id, student_id=request.user.id)	
        examwork.publish = True
        examwork.publication_date = timezone.now()
        questions = ExamQuestion.objects.filter(exam_id=exam_id).order_by("id")	
        question_ids = []
        score = 0
        for question in questions:
            question_ids.append(question.id)		
        answer_dict = dict(((answer.question_id, answer.answer) for answer in ExamAnswer.objects.filter(examwork_id=examwork_id, question_id__in=question_ids, student_id=request.user.id)))		
        for question in questions:
            if question.id in answer_dict:
                if question.answer == answer_dict[question.id] :
                    score += question.score		                 
        examwork.score = score
        examwork.scorer = 0
        examwork.save()
    return redirect('/student/exam/score/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/'+str(request.user.id)+'/0')

def exam_score(request, classroom_id, exam_id, examwork_id, user_id, question_id):
    score = 0
    score_total = 0
    exam = Exam.objects.get(id=exam_id)
    try:
        examwork = ExamWork.objects.get(id=examwork_id)
    except ObjectDoesNotExist:
        pass
    question_ids = examwork.questions.split(',')
    score_answer = dict(((question.id, [question.score, question.answer]) for question in ExamQuestion.objects.filter(exam_id=exam_id)))			
    qas = []
    for question in question_ids:
        score_total += score_answer[int(question)][0]
    answer_dict = dict(((answer.question_id, [answer.answer, answer.answer_right]) for answer in ExamAnswer.objects.filter(examwork_id=examwork_id, question_id__in=question_ids, student_id=user_id)))		
    for question in question_ids:
        question = int(question)
        if question in answer_dict:
            if score_answer[question][1] == answer_dict[question][0] or answer_dict[question][1]:
                score += score_answer[question][0]
            qas.append([question, score_answer[question][1], answer_dict[question]])
        else :
            qas.append([question, score_answer[question][1], []])
    if not question_id == 0:
        question = ExamQuestion.objects.get(id=question_id)
    else :
        return redirect('/student/exam/score/'+str(classroom_id)+'/'+str(exam_id)+'/'+str(examwork_id)+'/'+str(user_id)+"/"+str(question_ids[0]))
    try :
        answer = ExamAnswer.objects.get(examwork_id=examwork_id, question_id=question_id, student_id=user_id).answer
    except ObjectDoesNotExist:
        answer = 0

    return render(request,'student/exam_score.html', {'user_id':user_id, 'classroom_id':classroom_id, 'examwork': examwork, 'score_total': score_total, 'score':score, 'question':question, 'answer':answer, 'exam':exam, 'qas':qas})
			
# 點擊影片觀看記錄
def video_log(request):
    # 記錄系統事件
    message = request.POST.get('log')
    youtube_id = request.POST.get('youtube_id')
    log = Log(user_id=request.user.id, youtube_id=youtube_id, event=message)
    log.save()
    return JsonResponse({'status':'ok'}, safe=False)

# 列出所有合作任務
class TeamListView(ListView):
    model = TeamWork
    context_object_name = 'teams'
    template_name = 'student/team_list.html'    
    
    def get_queryset(self):
        queryset = []
        classroom_id = self.kwargs['classroom_id']
        works = TeamWork.objects.filter(classroom_id=classroom_id).order_by("-id")
        for work in works:
            try:
                enroll = Enroll.objects.get(classroom_id=self.kwargs['classroom_id'], student_id=self.request.user.id)
                group = TeamClass.objects.get(team_id=work.id, classroom_id=self.kwargs['classroom_id']).group
            except ObjectDoesNotExist:
                group = 0
            queryset.append([work, group])
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super(TeamListView, self).get_context_data(**kwargs)
        context['classroom_id'] = self.kwargs['classroom_id']
        return context	    

def team_stage(request, classroom_id, grouping, team_id):
    enrolls = Enroll.objects.filter(classroom_id=classroom_id)
    enroll_dict = {}
    for enroll in enrolls:
        enroll_dict[enroll.id] = enroll
    groupclass_list = []  
    groupclass_dict = {}       
    student_ids = {}
    if grouping == "0":
        counter = 0
        for enroll in enrolls:
            groupclass_dict[counter] = [enroll_dict[enroll.id]]  
            counter +=1
    else:
        try:
            numbers = ClassroomGroup.objects.get(id=grouping).numbers
            for i in range(numbers):
                groupclass_dict[i] = []
                students = StudentGroup.objects.filter(group_id=grouping, group=i)
                for student in students:                    
                    if student.enroll_id in enroll_dict:
                        groupclass_dict[i].append(enroll_dict[student.enroll_id])            
        except ObjectDoesNotExist:
            counter = 0
            for enroll in enrolls:
                groupclass_dict[counter]= [enroll]  
                counter += 1          
    group_list = []
    for key in groupclass_dict:
        try: 
            leader_id = StudentGroupLeader.objects.get(group_id=grouping, group=key).enroll_id
            leader = Enroll.objects.get(id=leader_id)
        except ObjectDoesNotExist:
            leader_id = 0
            leader = None        
        if grouping == "0":
            teamworks = TeamContent.objects.filter(team_id=team_id, user_id=groupclass_dict[key][0].student_id, publish=True)
        else:
            members = groupclass_dict[key]
            student_ids = []
            for member in members:
                student_ids.append(member.student_id)
            teamworks = TeamContent.objects.filter(team_id=team_id, user_id__in=student_ids, publish=True)
        groupclass_list.append([key, leader, groupclass_dict[key], len(teamworks)])    

    teamclass = TeamClass.objects.get(team_id=team_id, classroom_id=classroom_id)
    try:
        group = ClassroomGroup.objects.get(id=teamclass.group)
    except ObjectDoesNotExist:
        group = ClassroomGroup(title="不分組", id=0)
    return render(request,'student/team_stage.html',{'grouping': grouping, 'groups': groupclass_list, 'team_id': team_id, 'classroom_id':classroom_id})

# 列出所有合作任務素材
class TeamContentListView(ListView):
    model = TeamContent
    context_object_name = 'contents'
    template_name = "student/team_content.html"		
    def get_queryset(self):
        if self.kwargs['grouping'] == "0":
            group_id = 0
        else:
            enroll_id = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id']).id
            group_id = StudentGroup.objects.get(group_id=self.kwargs['grouping'], enroll_id=enroll_id).group
        publish = self.kwargs['publish']
        user_ids = []        
        enrolls = StudentGroup.objects.filter(group_id=self.kwargs['grouping'], group=group_id)
        if len(enrolls) > 0:           
            for enroll in enrolls:
                student_id = Enroll.objects.get(id=enroll.enroll_id).student_id
                user_ids.append(student_id)
        else:
            if self.kwargs['stage'] != "0":
                try:
                    enroll = Enroll.objects.get(id=self.kwargs['stage'])
                    user_ids.append(enroll.student_id)
                except ObjectDoesNotExist:
                    pass
            else:
                user_ids.append(self.request.user.id)       
        if publish == "0":
            queryset = TeamContent.objects.filter(team_id=self.kwargs['team_id'], user_id__in=user_ids).order_by("-id")
        else :
            queryset = TeamContent.objects.filter(team_id=self.kwargs['team_id'], user_id__in=user_ids, publish=True).order_by("-id")          
        return queryset
			
    def get_context_data(self, **kwargs):
        context = super(TeamContentListView, self).get_context_data(**kwargs)
        teamwork = TeamWork.objects.get(id=self.kwargs['team_id'])
        context['teamwork']= teamwork
        context['team_id'] = self.kwargs['team_id']
        context['grouping'] = self.kwargs['grouping']
        context['classroom_id'] = self.kwargs['classroom_id']
        if self.kwargs['grouping'] == "0":
            group_id = 0
        else :
            group_id = TeamClass.objects.get(team_id=self.kwargs['team_id'], classroom_id=self.kwargs['classroom_id']).group
        try:  
            enroll = Enroll.objects.get(student_id=self.request.user.id, classroom_id=self.kwargs['classroom_id'])
            leader = StudentGroupLeader.objects.get(group_id=group_id, enroll_id=enroll.id)
            mygroup = StudentGroup.objects.get(group_id=group_id, enroll_id=enroll.id)
            if leader.group == mygroup.group:
                context['leader'] = True
            else:
                context['leader'] = False
        except ObjectDoesNotExist:
            context['leader'] = False
        enroll_id = Enroll.objects.get(classroom_id=self.kwargs['classroom_id'], student_id=self.request.user.id).id
        try:
            group = StudentGroup.objects.get(enroll_id=enroll_id, group_id=group_id).group
        except ObjectDoesNotExist:
            context['leader'] = True
        return context	
            
#新增一個素材
class TeamContentCreateView(CreateView):
    model = TeamContent
    form_class = TeamContentForm
    template_name = "student/team_content_form.html"
    def form_valid(self, form):
        self.object = form.save(commit=False)
        work = TeamContent(team_id=self.object.team_id)
        if self.object.types == 1:
            work.types = 1
            work.title = self.object.title
            work.link = self.object.link
        if self.object.types  == 2:
            work.types = 2					
            work.youtube = self.object.youtube
        if self.object.types  == 3:
            work.types = 3
            myfile = self.request.FILES['content_file']
            fs = FileSystemStorage()
            filename = uuid4().hex
            work.title = myfile.name
            work.filename = str(self.request.user.id)+"/"+filename
            fs.save("static/upload/"+str(self.request.user.id)+"/"+filename, myfile)
        if self.object.types  == 4:
            work.types = 4
        work.memo = self.object.memo
        work.user_id = self.request.user.id
        work.save()         
  
        return redirect("/student/team/content/"+self.kwargs['classroom_id']+"/"+self.kwargs['grouping']+"/"+self.kwargs['team_id']+"/0/0")  

    def get_context_data(self, **kwargs):
        ctx = super(TeamContentCreateView, self).get_context_data(**kwargs)
        ctx['team'] = TeamWork.objects.get(id=self.kwargs['team_id'])
        return ctx

def team_delete(request, classroom_id, grouping,  team_id, content_id):
    instance = TeamContent.objects.get(id=content_id)
    instance.delete()

    return redirect("/student/team/content/"+classroom_id+"/"+{{gropuing}}+"/"+team_id+"/0/0")  
	
def team_edit(request, classroom_id, grouping, team_id, content_id):
    try:
        instance = TeamContent.objects.get(id=content_id)
    except:
        pass
    if request.method == 'POST':
            content_id = request.POST.get("id", "")
            try:
                content = TeamContent.objects.get(id=content_id)
            except ObjectDoesNotExist:
	              content = TeamContent(forum_id= request.POST.get("forum_id", ""), types=form.cleaned_data['types'])
            if content.types == 1:
                content.title = request.POST.get("title", "")
                content.link = request.POST.get("link", "")
            elif content.types == 2:
                content.youtube = request.POST.get("youtube", "")
            elif content.types == 3:
                myfile =  request.FILES.get("content_file", "")
                fs = FileSystemStorage()
                filename = uuid4().hex
                content.title = myfile.name
                content.filename = str(request.user.id)+"/"+filename
                fs.save("static/upload/"+str(request.user.id)+"/"+filename, myfile)
            content.memo = request.POST.get("memo", "")
            content.save()
            return redirect('/student/team/content/'+classroom_id+'/'+grouping+"/"+team_id+"/0/0")   
    return render(request,'student/team_edit.html',{'content': instance, 'team_id':team_id, 'content_id':content_id})		
	
# Ajax 設為發表、取消發表
def team_make_publish(request):
    work_id = request.POST.get('workid')
    action = request.POST.get('action')
    if work_id and action :
        if action == 'set':            
            try :
                work = TeamContent.objects.get(id=work_id) 	
                work.publish = True
                work.save()
            except ObjectDoesNotExist :
                pass
        else : 
            try :
                work = TeamContent.objects.get(id=work_id) 				
                work.publish = False
                work.save()
            except ObjectDoesNotExist :
                pass             
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'fail'}, safe=False)

# 測驗卷
def exam(request):
    # 限登入者
    if not request.user.is_authenticated:
        return redirect("/account/login/")
    else :
        return render(request, 'student/exam.html')

# 測驗卷得分
def exam_score(request):
    exams = ScratchExam.objects.filter(student_id=request.user.id).order_by("-id")
    return render(request, 'student/scratchexam_score.html', {'exams':exams} )

# 測驗卷檢查答案
def exam_check(request):
    exam_id = request.POST.get('examid')
    user_answer = request.POST.get('answer').split(",")
    if not exam_id in ["1", "2", "3"]:
        return JsonResponse({'status':'ko'}, safe=False)

    correct_answer_list = ["C,A,D,C,C,A,B,B,D,D", "B,C,C,A,D,B,A,D,B,C", "D,C,A,B,D,C,D,A,D,B"]
    answer = correct_answer_list[int(exam_id)-1]
    correct_answer = answer.split(",")
    ua_test = ""
    score = 0
    for i in range(10) :
        if user_answer[i] == correct_answer[i] :
            score = score + 10
    ua_test = "".join(user_answer)
    exam = ScratchExam(exam_id=int(exam_id), student_id=request.user.id, answer=ua_test, score=score)
    exam.save()
    return JsonResponse({'status':'ok','answer':answer}, safe=False)