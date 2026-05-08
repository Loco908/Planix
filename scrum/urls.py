from django.urls import path
from . import views

app_name = 'scrum'

urlpatterns = [
    path('project/<int:project_id>/story/create/', views.UserStoryCreateView.as_view(), name='story_create'),
    path('story/<int:pk>/edit/', views.UserStoryUpdateView.as_view(), name='story_edit'),
    path('story/<int:pk>/delete/', views.UserStoryDeleteView.as_view(), name='story_delete'),
]
