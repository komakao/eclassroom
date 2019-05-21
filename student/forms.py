from django import forms
from student.models import *

class EnrollForm(forms.ModelForm): 
    password = forms.CharField()

    class Meta:
        model = Enroll
        fields = ('seat', 'computer')
        
    def __init__(self, *args, **kwargs):
        super(EnrollForm, self).__init__(*args, **kwargs)  
        self.fields['password'].label = "選課密碼"
        self.fields['seat'].label = "座號"
        self.fields['computer'].label = "電腦"        
		
class SubmitAForm(forms.ModelForm):
        class Meta:
           model = Work
           fields = ['file','memo']
           
        def __init__(self, *args, **kwargs):
            super(SubmitAForm, self).__init__(*args, **kwargs)
            self.fields['file'].label = "作品檔案"
            self.fields['memo'].label = "心得感想"

class SeatForm(forms.ModelForm):
        class Meta:
            model = Enroll
            fields = ['seat']			
			
class ComputerForm(forms.ModelForm):
        class Meta:
            model = Enroll
            fields = ['computer']	

class ForumSubmitForm(forms.ModelForm):
    class Meta:
        model = SFWork
        fields = ['memo','memo_e', 'memo_c']  
      
    def __init__(self, *args, **kwargs):
        super(ForumSubmitForm, self).__init__(*args, **kwargs)
        self.fields['memo'].label = "心得感想"
        self.fields['memo_e'].label = "英文"
        self.fields['memo_c'].label = "中文"            
        #self.fields['file'].label = "檔案"
		
class SpeculationSubmitForm(forms.Form):
        memo =  forms.CharField(required=False)
        file = forms.FileField(required=False)
      
        def __init__(self, *args, **kwargs):
            super(SpeculationSubmitForm, self).__init__(*args, **kwargs)
            self.fields['memo'].label = "心得感想"
            self.fields['file'].label = "檔案"

# 新增一個作業
class TeamContentForm(forms.ModelForm):
        class Meta:
           model = TeamContent
           fields = ['team_id', 'types', 'title', 'link', 'youtube', 'file', 'memo']
        
        def __init__(self, *args, **kwargs):
            super(TeamContentForm, self).__init__(*args, **kwargs)
            self.fields['team_id'].required = False		
            self.fields['title'].required = False						
            self.fields['link'].required = False
            self.fields['youtube'].required = False
            self.fields['file'].required = False
            self.fields['memo'].required = False	
