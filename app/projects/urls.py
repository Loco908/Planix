from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/members/add/', views.ProjectMemberCreateView.as_view(), name='add_member'),
    path('member/<int:member_id>/edit/', views.ProjectMemberUpdateView.as_view(), name='edit_member'),
    path('member/<int:member_id>/delete/', views.ProjectMemberDeleteView.as_view(), name='delete_member'),
]
