
from django import forms
from django.shortcuts import get_object_or_404, redirect
from .models import Topic, Card
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']  # The field for adding a new topic

class CardCheckForm(forms.Form):
    card_id = forms.IntegerField(required=True)
    solved = forms.BooleanField(required=False)


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
