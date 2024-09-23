
from django import forms
from django.shortcuts import get_object_or_404, redirect
from .models import Topic, Card

class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['name']  # The field for adding a new topic

class CardCheckForm(forms.Form):
    card_id = forms.IntegerField(required=True)
    solved = forms.BooleanField(required=False)


