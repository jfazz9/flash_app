# cards/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
        path(
        '', 
         HomeView.as_view(), 
         name='home'
    ),
    path(
        "cards/",
        CardListView.as_view(),
        name="card-list"
    ),

    path(
        "new/",
        CardCreateView.as_view(),
        name="card-create"
    ),
    path(
        "edit/<int:pk>",
        CardUpdateView.as_view(),
        name="card-update"),
    path(
        "box/<int:box_num>",
        BoxView.as_view(),
        name="box"),
    path(
        'topics/', 
         TopicListView.as_view(), 
         name='topic-list'),
    path(
        'card/<int:pk>/delete/', 
        CardDeleteView.as_view(), 
        name='card-delete'),
    path(
        'card/<int:pk>/submit-answer/',
        submit_answer, 
        name='submit-answer'),
    # Authentication
    path('signup/',
        signup, 
         name='signup'),
    path('login/',
         auth_views.LoginView.as_view(),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(next_page='home'),
         name='logout'),
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(), 
         name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(), 
         name='password_change_done'),
    path('accounts/profile/',
         profile,
         name='profile')
]