# cards/urls.py

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path(
        "",
        views.CardListView.as_view(),
        name="card-list"
    ),
    path(
        "new",
        views.CardCreateView.as_view(),
        name="card-create"
    ),
    path(
        "edit/<int:pk>",
        views.CardUpdateView.as_view(),
        name="card-update"),
    path(
        "box/<int:box_num>",
        views.BoxView.as_view(),
        name="box"),
    path(
        'topics/', 
         views.TopicListView.as_view(), 
         name='topic-list'),
    path(
        'card/<int:pk>/delete/', 
        views.CardDeleteView.as_view(), 
        name='card-delete'),
    path(
        'card/<int:pk>/submit-answer/',
        views.submit_answer, 
        name='submit-answer'),
    path('signup/',
         views.signup, 
         name='signup'),
    path('login/',
         auth_views.LoginView.as_view(),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),
    path('password_change/', 
         auth_views.PasswordChangeView.as_view(), 
         name='password_change'),
    path('password_change/done/', 
         auth_views.PasswordChangeDoneView.as_view(), 
         name='password_change_done')
]