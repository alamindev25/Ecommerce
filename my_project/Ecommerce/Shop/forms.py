from django import forms 
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm,UsernameField,PasswordChangeForm,PasswordResetForm
from django.contrib.auth.models import User
from django.utils.translation import gettext,gettext_lazy as _
from django.contrib.auth import password_validation
 # Registration
 
class CustomerRegistrationForm(UserCreationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 =forms.CharField(label='password',widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2=forms.CharField(label='confirm password',widget=forms.PasswordInput(attrs={'class':'form-control'}))
    email=forms.CharField(required=True,widget=forms.EmailInput(attrs={'class':'form-control'}))

    class Meta:
        model =User
        fields =['username','email','password1','password2']
        labels= {'email':'Email'}
        widgets={'username': forms.TextInput(attrs={'class': 'form-control'})}
#login
class LoginForm(AuthenticationForm):
    username=UsernameField(widget=forms.TextInput(attrs={'autofouse':True,'class':'form-control'}))
    password=forms.CharField(label=_('Password'), strip='False',widget=forms.PasswordInput(attrs={ 'autocomplete':'current_password','class': 'form-control'})) 

#password change
class MyPasswordChangeForm(PasswordChangeForm):
    old_password=forms.CharField(label=_('old_Password'), strip='False',widget=forms.PasswordInput(attrs={'autocomplete':'current_password','autofouse':True,'class':'form-control'}))
    new_password1=forms.CharField(label=_('new password'),widget=forms.PasswordInput(attrs={'autocomplete':'new_password','class':'form-control'}),help_text=password_validation.password_validators_help_text_html())
    new_password2=forms.CharField(label=_('confirm new password'),widget=forms.PasswordInput(attrs={'autocomplete':'new_password','class':'form-control'}))

#Reset
class MyPasswordReset(PasswordResetForm):
    email=forms.EmailField(label=_("Email"),max_length=50,widget=forms.EmailInput(attrs={'autocomplete':'email','class':'form-control'}))
    
    
    
    