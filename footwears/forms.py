
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
  email = forms.EmailField()
  number = forms.CharField()

  class Meta:
    model = User
    fields = ['username','email','number','password1','password2']

  def save(self, commit=True):
    user = super().save(commit=False)

    user.email = self.cleaned_data['email']
    user.number = self.cleaned_data['number']

    if commit:
      user.save()
    return user


