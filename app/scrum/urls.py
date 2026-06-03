from django.urls import path
from . import views

app_name = 'scrum'

urlpatterns = [
    path('project/<int:project_id>/story/create/', views.UserStoryCreateView.as_view(), name='story_create'),
    path('story/<int:pk>/edit/', views.UserStoryUpdateView.as_view(), name='story_edit'),
    path('story/<int:pk>/delete/', views.UserStoryDeleteView.as_view(), name='story_delete'),
    
    # Sprints
    path('project/<int:project_id>/sprints/', views.SprintListView.as_view(), name='sprint_list'),
    path('project/<int:project_id>/sprint/create/', views.SprintCreateView.as_view(), name='sprint_create'),
    path('sprint/<int:pk>/edit/', views.SprintUpdateView.as_view(), name='sprint_edit'),
    
    # Kanban y Tickets
    path('sprint/<int:sprint_id>/kanban/', views.KanbanView.as_view(), name='kanban'),
    path('sprint/<int:sprint_id>/ticket/create/', views.TicketCreateView.as_view(), name='ticket_create'),
    path('ticket/<int:pk>/edit/', views.TicketUpdateView.as_view(), name='ticket_edit'),
    path('ticket/<int:pk>/delete/', views.TicketDeleteView.as_view(), name='ticket_delete'),
    path('ticket/<int:pk>/status/', views.TicketStatusUpdateView.as_view(), name='ticket_status'),
]
