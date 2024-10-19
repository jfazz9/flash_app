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
from .forms import CardCheckForm, TopicForm, SignUpForm, CardForm, FlashcardImportForm
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
import random, re


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

class CardListView(LoginRequiredMixin, ListView):
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
        context['topics'] = Topic.objects.filter(user=self.request.user)
        context['selected_topic'] = self.request.GET.get('topic')
        # Add the user-specific box counts
        context['boxes'] = get_user_box_counts(self.request.user)
        return context


class CardCreateView(LoginRequiredMixin,CreateView):
    model = Card
    form_class = CardForm
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

class BoxView(LoginRequiredMixin, ListView):
    model = Card
    template_name = "cards/box.html"
    form_class = CardCheckForm
    login_url = reverse_lazy('login')

    def get_queryset(self):
        self.queryset = Card.objects.filter(box=self.kwargs["box_num"], user=self.request.user)
        topic_id = self.request.GET.get('topic')

        if topic_id:
            self.queryset = self.queryset.filter(topic__id=topic_id)
        
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["box_number"] = self.kwargs["box_num"]
        context["topics"] = Topic.objects.filter(user=self.request.user)
        context['selected_topic'] = self.request.GET.get('topic')
        context['boxes'] = Card.objects.filter(user=self.request.user)

        queryset = self.get_queryset()
        if queryset.exists():
            context["check_card"] = random.choice(queryset)
        context["form"] = self.form_class()  # Initialize the form in the context
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            card = get_object_or_404(Card, id=form.cleaned_data["card_id"])
            card.move(form.cleaned_data["solved"])
        return redirect(request.META.get("HTTP_REFERER"))

class TopicListView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'topics/topic_list.html'
    context_object_name = 'topics'

    def get_queryset(self):
        return Topic.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TopicForm()  # Form to add a new topic
        return context

    def post(self, request, *args, **kwargs):
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user
            topic.save()
            return redirect('topic-list')
        else:
            # Handle invalid form submission, re-render the template with form errors
            return self.get(request)  # Re-render with the original GET method to display errors

class TopicDelete(LoginRequiredMixin, DeleteView):
    model = Topic  # You can use the Topic model
    template_name = 'cards/topic_confirm_delete.html'
    success_url = reverse_lazy('flashcards')  # Redirect after successful deletion

    def get_queryset(self):
        # Ensure the user can only delete topics they own
        return Topic.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        # Override the delete method to delete related Cards first
        topic = self.get_object()

        # Delete all Cards associated with this Topic for the logged-in user
        Card.objects.filter(topic=topic, user=self.request.user).delete()

        # Optionally, delete the topic itself
        return super().delete(request, *args, **kwargs)


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

@login_required
def import_flashcards(request):
    if request.method == 'POST':
        form = FlashcardImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            topic_name = form.cleaned_data['topic_name']

            # Find or create the topic by name and associate it with the logged-in user
            topic, created = Topic.objects.get_or_create(
                name=topic_name,
                defaults={'user': request.user}
            )

            try:
                # Read and decode the uploaded file
                text = file.read().decode('utf-8')

                # Regex pattern to match questions and answers
                pattern = r'(\d+\.\s.*?\?)\s*(-\s.*?)(?=\d+\.|$)'
                matches = re.findall(pattern, text, re.DOTALL)

                # Iterate over matches and save them as flashcards
                for i, (question, answer) in enumerate(matches, 1):
                    question = question.strip()
                    answer = answer.strip().lstrip('-').strip()

                        # Create and save the Card object
                    Card.objects.create(
                        user=request.user,
                        question=question,
                        answer=answer,
                        box=1,
                        topic=topic
                    )

                return redirect('home')

            except Exception as e:
                return render(request, 'cards/import.html', {'form': form, 'error': f'Error processing file: {e}'})
    else:
        form = FlashcardImportForm()

    return render(request, 'cards/import.html', {'form': form})

@login_required
def manage_topics(request):
    if request.method == 'POST':
        # Check if the request is for topic deletion
        if 'topic' in request.POST:  # This indicates that the deletion form was submitted
            topic_id = request.POST.get('topic')
            topic = get_object_or_404(Topic, id=topic_id, user=request.user)
            
            # Delete all Cards related to this Topic for the current user
            Card.objects.filter(topic=topic, user=request.user).delete()

            # Optionally, delete the topic itself
            topic.delete()

            return redirect('topic-list')  # Redirect to refresh the page after deletion

        # If not a delete request, it must be a topic creation request
        form = TopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.user = request.user  # Assign the logged-in user
            topic.save()
            return redirect('manage-topics')
    else:
        form = TopicForm()

    # Fetch all topics for the logged-in user
    topics = Topic.objects.filter(user=request.user)
    return render(request, 'topics/manage_topics.html', {'form': form, 'topics': topics})