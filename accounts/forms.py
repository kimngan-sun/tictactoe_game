from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm 
from django.contrib.auth import get_user_model 
from django_recaptcha.fields import ReCaptchaField 
from django_recaptcha.widgets import ReCaptchaV2Checkbox 

#Form đăng ký
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='Nhập email',required=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name','last_name','username','email','password1','password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

#Form đăng nhập
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control','placeholder': 'Username hoặc Email'}),
        label = 'Username hoặc Email')
    
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class':'form-control','placeholder': 'Password'}))
    
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
                            
#Form profile
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = get_user_model()
        fields = ['first_name','last_name','email','description']

#
class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

