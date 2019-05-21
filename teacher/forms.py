from django import forms
from account.models import *
from teacher.models import *
from student.models import *
from django.forms import modelformset_factory

#上傳檔案
class UploadFileForm(forms.Form):
    file = forms.FileField()
	
# 新增一個分組表單
class GroupForm(forms.ModelForm):
        class Meta:
           model = ClassroomGroup
           fields = ['title','numbers', 'assign']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "分組名稱"							
            self.fields['numbers'].label = "分組數目"	
						
# 新增一個分組表單
class GroupForm2(forms.ModelForm):
        class Meta:
           model = ClassroomGroup
           fields = ['title','numbers']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm2, self).__init__(*args, **kwargs)
            self.fields['title'].label = "分組名稱"							
            self.fields['numbers'].label = "分組數目"		
			
						
# 新增一個繳交期長表單
class ForumDeadlineForm(forms.ModelForm):
        class Meta:
           model = FClass
           fields = ['deadline', 'deadline_date']
        
        def __init__(self, *args, **kwargs):
            super(ForumDeadlineForm, self).__init__(*args, **kwargs)			

						
# 新增一個作業
class ForumForm(forms.ModelForm):
        class Meta:
           model = FWork
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(ForumForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "討論主題"
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})									
						
# 新增一個作業
class ForumContentForm(forms.ModelForm):
        class Meta:
           model = FContent
           fields = ['forum_id', 'types', 'title', 'link', 'youtube', 'file', 'memo']
        
        def __init__(self, *args, **kwargs):
            super(ForumContentForm, self).__init__(*args, **kwargs)
            self.fields['forum_id'].required = False		
            self.fields['title'].required = False						
            self.fields['link'].required = False
            self.fields['youtube'].required = False
            self.fields['file'].required = False
            self.fields['memo'].required = False						
						
# 新增一個課程表單
class AnnounceForm(forms.ModelForm):
        class Meta:
           model = Message
           fields = ['title', 'content']
        
        def __init__(self, *args, **kwargs):
            super(AnnounceForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "公告主旨"
            self.fields['title'].widget.attrs['size'] = 50	
            self.fields['content'].required = False							
            self.fields['content'].label = "公告內容"
            self.fields['content'].widget.attrs['cols'] = 50
            self.fields['content'].widget.attrs['rows'] = 20        
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})      			

# 新增一個作業
class WorkForm(forms.ModelForm):
        class Meta:
           model = TWork
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(WorkForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "作業名稱"

			
		
# 作業評分表單           
class ScoreForm(forms.ModelForm):
        RELEVANCE_CHOICES = (
            (100, "你好棒(100分)"),
            (90, "90分"),
            (80, "80分"),
            (70, "70分"),
            (60, "60分"),
			(-1, "重交")
        )
        score = forms.ChoiceField(choices = RELEVANCE_CHOICES, required=True, label="分數")
        #if user.groups.all()[0].name == 'teacher': 
        assistant = forms.BooleanField(required=False,label="小老師")
    
        class Meta:
           model = Work
           fields = ['score', 'comment']
		   
        def __init__(self, user, *args, **kwargs): 
            super(ScoreForm, self).__init__(*args, **kwargs)
            self.fields['comment'].required = False				
            self.initial['score'] = 100		
            if user.groups.all().count() == 0 :
                del self.fields['assistant']			

Check_CHOICES = (
    (100, "你好棒(100分)"),
    (90, "90分"),
    (80, "80分"),
    (70, "70分"),
    (60, "60分"),
    (40, "40分"),
    (20, "20分"),
    (0, "0分"),
)    

				
class CheckForm(forms.ModelForm):
        score_memo0 = forms.ChoiceField(choices = Check_CHOICES, required=True, label="全部分數")
        score_memo1 = forms.ChoiceField(choices = Check_CHOICES, required=True, label="上學期分數")
        score_memo2 = forms.ChoiceField(choices = Check_CHOICES, required=True, label="下學期分數")            

        class Meta:
           model = Enroll
           fields = ['score_memo0', 'score_memo1', 'score_memo2']
		   
class CheckForm2(forms.ModelForm):
        score_memo0_custom = forms.ChoiceField(choices = Check_CHOICES, required=True, label="全部分數")
        score_memo1_custom = forms.ChoiceField(choices = Check_CHOICES, required=True, label="上學期分數")
        score_memo2_custom = forms.ChoiceField(choices = Check_CHOICES, required=True, label="下學期分數")            

        class Meta:
           model = Enroll
           fields = ['score_memo0_custom', 'score_memo1_custom', 'score_memo2_custom']

# 新增一個測驗
class ExamForm(forms.ModelForm):
        class Meta:
           model = Exam                    
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(ExamForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "測驗主題"
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})							
																		

# 新增一個繳交期長表單
class ExamDeadlineForm(forms.ModelForm):
        class Meta:
           model = ExamClass
           fields = ['deadline', 'deadline_date']
        
        def __init__(self, *args, **kwargs):
            super(ExamDeadlineForm, self).__init__(*args, **kwargs)								
						
# 新增一個題目
class ExamQuestionForm(forms.ModelForm):
        class Meta:
           model = ExamQuestion
           fields = ['exam_id', 'types', 'title', 'option1', 'option2', 'option3', 'option4', 'answer', 'score']
        
        def __init__(self, *args, **kwargs):
            super(ExamQuestionForm, self).__init__(*args, **kwargs)
            self.fields['exam_id'].required = False		
            self.fields['title'].required = False						
            self.fields['option1'].required = False
            self.fields['option2'].required = False
            self.fields['option3'].required = False
            self.fields['option4'].required = False
            self.fields['answer'].required = False			
            self.fields['score'].required = False				


# 新增一個文章
class SpeculationForm(forms.ModelForm):
        class Meta:
           model = SpeculationWork
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(SpeculationForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "文章主題"
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})									
						
# 新增一個文章
class SpeculationContentForm(forms.ModelForm):
        class Meta:
           model = SpeculationContent
           fields = ['forum_id', 'types', 'text', 'youtube', 'file', 'memo', 'title', 'link']
        
        def __init__(self, *args, **kwargs):
            super(SpeculationContentForm, self).__init__(*args, **kwargs)
            self.fields['forum_id'].required = False		
            self.fields['text'].required = False
            self.fields['youtube'].required = False
            self.fields['file'].required = False
            self.fields['memo'].required = False						
            self.fields['link'].required = False
            self.fields['title'].required = False					
						
# 新增一個繳交期限表單
class SpeculationDeadlineForm(forms.ModelForm):
        class Meta:
           model = SpeculationClass
           fields = ['deadline', 'deadline_date']
        
        def __init__(self, *args, **kwargs):
            super(SpeculationDeadlineForm, self).__init__(*args, **kwargs)									

# 新增一個註記類別
class SpeculationAnnotationForm(forms.ModelForm):
        class Meta:
           model = SpeculationAnnotation
           fields = ['forum_id', 'kind', 'color']
        
        def __init__(self, *args, **kwargs):
            super(SpeculationAnnotationForm, self).__init__(*args, **kwargs)
						
# 新增一個分組表單
class GroupForm(forms.ModelForm):
        class Meta:
           model = ClassroomGroup
           fields = ['title','numbers', 'assign']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "分組名稱"							
            self.fields['numbers'].label = "分組數目"	
						
# 新增一個分組表單
class GroupForm2(forms.ModelForm):
        class Meta:
           model = ClassroomGroup
           fields = ['title','numbers']
        
        def __init__(self, *args, **kwargs):
            super(GroupForm2, self).__init__(*args, **kwargs)
            self.fields['title'].label = "分組名稱"							
            self.fields['numbers'].label = "分組數目"	

# 新增一個測驗
class ExamForm(forms.ModelForm):
        class Meta:
           model = Exam                    
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(ExamForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "測驗主題"
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})							
																					

# 新增一個繳交期長表單
class ExamDeadlineForm(forms.ModelForm):
        class Meta:
           model = ExamClass
           fields = ['deadline', 'deadline_date']
        
        def __init__(self, *args, **kwargs):
            super(ExamDeadlineForm, self).__init__(*args, **kwargs)								
						
# 新增一個題目
class ExamQuestionForm(forms.ModelForm):
        class Meta:
           model = ExamQuestion
           fields = ['exam_id', 'types', 'title', 'title_pic', 'option1', 'option2', 'option3', 'option4', 'answer', 'score']
        
        def __init__(self, *args, **kwargs):
            super(ExamQuestionForm, self).__init__(*args, **kwargs)
            self.fields['exam_id'].required = False		
            self.fields['title'].required = True				
            self.fields['title_pic'].required = False	            		
            self.fields['option1'].required = False
            self.fields['option2'].required = False
            self.fields['option3'].required = False
            self.fields['option4'].required = False
            self.fields['answer'].required = False					                                    
            self.fields['score'].required = True				


#上傳檔案
class UploadFileForm(forms.Form):
    file = forms.FileField()						
		
# 新增一個任務
class TeamForm(forms.ModelForm):
        class Meta:
           model = TeamWork
           fields = ['title']
        
        def __init__(self, *args, **kwargs):
            super(TeamForm, self).__init__(*args, **kwargs)
            self.fields['title'].label = "任務主題"
            self.fields['title'].widget.attrs.update({'class' : 'form-control list-group-item-text'})									
								
# 新增一個繳交期限表單
class TeamDeadlineForm(forms.ModelForm):
        class Meta:
           model = TeamClass
           fields = ['deadline', 'deadline_date']
        
        def __init__(self, *args, **kwargs):
            super(TeamDeadlineForm, self).__init__(*args, **kwargs)			

# 新增一個測驗分類表單
class ExamCategroyForm(forms.ModelForm):
        class Meta:
           model = Exam
           fields = ['domains', 'levels']
        
        def __init__(self, *args, **kwargs):
            super(ExamCategroyForm, self).__init__(*args, **kwargs)			