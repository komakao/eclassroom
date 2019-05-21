from django import forms
from django.contrib.auth.models import User, Group
from account.models import *
from captcha.fields import CaptchaField


# 使用者登入表單
class LoginForm(forms.Form):
    username = forms.CharField(label='帳號')
    password = forms.CharField(label='密碼', widget=forms.PasswordInput)

# 學生登入表單
class LoginStudentForm(forms.Form):
    teacher = forms.CharField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(LoginStudentForm, self).__init__(*args, **kwargs)
        self.fields['teacher'].label = "教師帳號"
        self.fields['username'].label = "學生帳號"
        self.fields['password'].label = "學生密碼"    

class UserRegistrationForm(forms.ModelForm): 
    error_messages = {
        'duplicate_username': ("此帳號已被使用")
    }
    
    username = forms.RegexField(
        label="User name", max_length=30, regex=r"^[\w.@+-]+$",
        error_messages={
            'invalid': ("帳號名稱無效")
        }
    )
    
    password = forms.CharField(label='Password', 
                               widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', 
                                widget=forms.PasswordInput)
    captcha = CaptchaField(error_messages={'invalid': '驗證碼錯誤'})
	
    class Meta:
        model = User
        fields = ('username',)

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
            
    def clean_username(self):
        username = self.cleaned_data["username"]
        if self.instance.username == username:
            return username
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "帳號"
        #self.fields['first_name'].label = "暱稱"
        self.fields['password'].label = "密碼"
        self.fields['password2'].label = "再次確認密碼" 
        self.fields['captcha'].label = "驗證碼"

class UserUpdateForm(forms.ModelForm): 
    class Meta:
        model = User
        fields = ('username', 'first_name')

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "帳號"
        self.fields['first_name'].label = "暱稱"         

class UserPasswordForm(forms.ModelForm): 
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('password',)
        
    def __init__(self, *args, **kwargs):
        super(UserPasswordForm, self).__init__(*args, **kwargs)  
        self.fields['password'].label = "密碼"
        
class UserTeacherForm(forms.Form):    
    teacher = forms.BooleanField(required=False)
       
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('pk', None)
        super(UserTeacherForm, self).__init__(*args, **kwargs)  
        self.fields['teacher'].label = "教師"  
        self.fields['teacher'].initial = User.objects.get(id=user_id).groups.filter(name='teacher').exists()
        
# 新增一個私訊表單
class LineForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title','content',]
       
    def __init__(self, *args, **kwargs):
        super(LineForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = "主旨"
        self.fields['title'].widget.attrs['size'] = 50
        self.fields['content'].label = "內容"
        self.fields['content'].required = False            
        self.fields['content'].widget.attrs['cols'] = 50
        self.fields['content'].widget.attrs['rows'] = 20          

# 修改密碼表單
class PasswordForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['password']

# 修改暱稱表單
class NicknameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name']

    def __init__(self, *args, **kwargs):
        super(NicknameForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = "暱稱"