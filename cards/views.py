# cards/views.py

from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from .models import Card, Topic, Flashcard
from .forms import CardCheckForm, TopicForm, SignUpForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
import random


class HomeView(TemplateView):
    template_name = 'cards/home.html'

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('home')
        else:
            messages.error(request, "Signup failed. Please try again.")

    else:
        form = SignUpForm()
    context = {
        "form":form
        }
    return render(request, 'cards/registration/signup.html', context)

def user_login(request):
    return render(request, 'login.html')

def submit_answer(request, pk):
    card = get_object_or_404(Card,pk=pk)
    if request.method == 'POST':
        user_answer = request.POST.get('user_answer', '').strip()

        if user_answer.lower() in card.answer.lower():
            solved = True
        else:
            solved = False
        card.move(solved)
        return redirect(request.META.get('HTTP_REFERER', 'card-list'))

def get_user_box_counts(user):
    """Returns the boxes and card counts for a specific user."""
    return Card.objects.filter(user=user).values('box').annotate(card_count=Count('id')).order_by('box')


class CardListView(ListView):
    model = Card
    template_name = 'cards/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        queryset = Card.objects.filter(user=self.request.user).order_by("box", "-date_created")
        topic_id = self.request.GET.get('topic')

        if topic_id:
            queryset = queryset.filter(topic__id=topic_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = Topic.objects.all()
        context['selected_topic'] = self.request.GET.get('topic')
        # Add the user-specific box counts
        context['boxes'] = get_user_box_counts(self.request.user)
        return context


class CardCreateView(LoginRequiredMixin,CreateView):
    model = Card
    fields = ['question', 'answer', 'box', 'topic']
    template_name = 'cards/card_form.html'
    success_url = reverse_lazy("card-create")
    login_url = reverse_lazy('login')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the user to the form
        return kwargs
    
    def form_valid(self, form):
        # Assign the logged-in user to the card
        form.instance.user = self.request.user
        messages.success(self.request, "Card successfully created!")
        return super().form_valid(form)


class CardUpdateView(CardCreateView, UpdateView):
    model = Card
    success_url = reverse_lazy("card-list")

    def get_object(self, queryset=None):
        card = get_object_or_404(Card, pk=self.kwargs['pk'], user=self.request.user)
        return card

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # Pass the user to the form
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, "Card successfully updated!")
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # Add this to see the form errors
        messages.error(self.request, "There was an error updating the card. Please try again.")
        return super().form_invalid(form)
    
class CardDeleteView(LoginRequiredMixin, DeleteView):
    model = Card
    success_url = reverse_lazy("card-list")
    template_name = 'cards/card_confirm_delete.html'

class BoxView(CardListView):
    model = Card
    template_name = "cards/box.html"
    form_class = CardCheckForm

    def get_queryset(self):
        queryset = Card.objects.filter(box=self.kwargs["box_num"], user=self.request.user)
        topic_id = self.request.GET.get('topic')

        if topic_id:
            queryset = queryset.filter(topic__id=topic_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_number"] = self.kwargs["box_num"]  # Current box number
        context["topics"] = Topic.objects.all()
        context['selected_topic'] = self.request.GET.get('topic')
        # Use the utility function to get user-specific box counts
        context['boxes'] = get_user_box_counts(self.request.user)

        # Randomly select a card to check
        queryset = self.get_queryset()
        if queryset.exists():
            context["check_card"] = random.choice(queryset)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            card = get_object_or_404(Card, id=form.cleaned_data["card_id"])
            card.move(form.cleaned_data["solved"])
        return redirect(request.META.get("HTTP_REFERER"))

class TopicListView(ListView):
    model = Topic
    template_name = 'topics/topic_list.html' 
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add an empty form to the context for adding topics
        context['topics'] = Topic.objects.filter(user=self.request.user)
        context['form'] = TopicForm()
        return context

    def post(self, request, *args, **kwargs):
        # Handle the POST request for adding a new topic
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('topic-list')  # Redirect to the same page after adding the topic
        else:
            topics = Topic.objects.filter(user=request.user)  # Get all topics to re-display them in case of form error
            return render(request, self.template_name, {'topics': topics, 'form': form})


'''filter views for user'''
@login_required(login_url=reverse_lazy('signup'))
def user_flashcards(request):
    user_flashcards = Flashcard.objects.filter(user=request.user)
    return render(request, 'flashcards.html', {'flashcards':user_flashcards})


def delete_flashcard(request, flashcard_id):
    flashcard = get_object_or_404(Flashcard, id=flashcard_id)
    if flashcard.user != request.user:
        return HttpResponseForbidden()  # Prevent the user from deleting another user's flashcard
    flashcard.delete()
    return redirect('user_flashcards')

@login_required
def profile(request):
    return render(request, 'cards/registration/profile.html')