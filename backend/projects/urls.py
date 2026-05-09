from django.urls import path

from .views import ProjectViewSet, ProjectMembersView

urlpatterns = [
    path('projects/', ProjectViewSet.as_view({'get': 'list', 'post': 'create'}), name='project-list'),
    path('projects/<int:pk>/', ProjectViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='project-detail'),

    # Admin-only: add member
    path(
        'projects/<int:project_id>/members/',
        ProjectMembersView.as_view({'post': 'post'}),
        name='project-members-add',
    ),

    # Admin-only: remove member
    path(
        'projects/<int:project_id>/members/<int:uid>/',
        ProjectMembersView.as_view({'delete': 'delete'}),
        name='project-members-remove',
    ),
]


