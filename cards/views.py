# cards/views.py

from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Card, Topic, Flashcard
from .forms import CardCheckForm, TopicForm, SignUpForm
import random
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request,user)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form':form})

def user_login(request):
    return render(request, 'login.html')


def submit_answer(request, pk):
    card = get_object_or_404(Card,pk=pk)
    if request.method == 'POST':
        user_answer = request.POST.get('user_answer', '').strip()

        if user_answer.lower() == card.answer.lower():
            solved = True
        else:
            solved = False
        card.move(solved)
        return redirect(request.META.get('HTTP_REFERER', 'card-list'))
    
class CardListView(ListView):
    model = Card
    template_name = 'cards/card_list.html'  # Ensure this points to your template
    context_object_name = 'cards'

    def get_queryset(self):
        # Start with the base queryset (all cards)
        queryset = Card.objects.all().order_by("box", "-date_created")
        
        # Get topic_id from the GET parameters (dropdown selection)
        topic_id = self.request.GET.get('topic')
        
        # If a topic is selected, filter cards by that topic
        if topic_id:
            queryset = queryset.filter(topic__id=topic_id)
        
        return queryset


    # def get_queryset(self):
    #     queryset = Card.objects.all()
    #     topic_id = self.request.GET.get('topic')
    #     if topic_id:
    #         queryset = queryset.filter(topic__id=topic_id)
    #     return queryset


    def get_context_data(self, **kwargs):
        # Add the topics to the context for the dropdown
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()  # Pass all topics to the template
        context['selected_topic'] = self.request.GET.get('topic')
        context['boxes'] = Card.objects.values('box').annotate(card_count=Count('id')).order_by('box')

        return context

class CardCreateView(CreateView):
    model = Card
    fields = ['question', 'answer', 'box', 'topic']
    success_url = reverse_lazy("card-create")

class CardUpdateView(CardCreateView, UpdateView):
    success_url = reverse_lazy("card-list")

class CardDeleteView(DeleteView):
    model = Card
    success_url = reverse_lazy("card-list")
    template_name = 'cards/card_confirm_delete.html'

class TopicListView(ListView):
    model = Topic
    template_name = 'topics/topic_list.html' 
    context_object_name = 'topics'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add an empty form to the context for adding topics
        context['form'] = TopicForm()
        return context

    def post(self, request, *args, **kwargs):
        # Handle the POST request for adding a new topic
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('topic-list')  # Redirect to the same page after adding the topic
        else:
            topics = Topic.objects.all()  # Get all topics to re-display them in case of form error
            return render(request, self.template_name, {'topics': topics, 'form': form})

class BoxView(CardListView):
    model = Card
    template_name = "cards/box.html"
    form_class = CardCheckForm

    def get_queryset(self):
        queryset = Card.objects.filter(box=self.kwargs["box_num"])

        topic_id = self.request.GET.get('topic')

        if topic_id:
            queryset = queryset.filter(topic__id=topic_id)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_number"] = self.kwargs["box_num"]  # Current box number
        context["topics"] = Topic.objects.all()
        context['selected_topic'] = self.request.GET.get('topic')
        context['boxes'] = Card.objects.values('box').annotate(card_count=Count('id')).order_by('box')
        # If there are cards in the queryset, pick a random one to check
        if self.object_list:
            context["check_card"] = random.choice(self.object_list)

        
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            card = get_object_or_404(Card, id=form.cleaned_data["card_id"])
            card.move(form.cleaned_data["solved"])
        return redirect(request.META.get("HTTP_REFERER"))


'''filter views for user'''
@login_required
def user_flashcards(request):
    user_flashcards = Flashcard.objects.filter(user=request.user)
    return render(request, 'flashcards.html', {'flashcards':user_flashcards})


def delete_flashcard(request, flashcard_id):
    flashcard = get_object_or_404(Flashcard, id=flashcard_id)
    if flashcard.user != request.user:
        return HttpResponseForbidden()  # Prevent the user from deleting another user's flashcard
    flashcard.delete()
    return redirect('user_flashcards')