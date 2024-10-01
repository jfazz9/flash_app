
from django import forms
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

class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['question', 'answer', 'box', 'topic']  # Your form fields

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Handle the 'user' argument safely
        super(CardForm, self).__init__(*args, **kwargs)
        # If the user is provided, filter the topics by that user
        if user:
            self.fields['topic'].queryset = Topic.objects.filter(user=user)


class SignUpForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
