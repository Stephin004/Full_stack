from django.urls import path

from .views import TaskViewSet

urlpatterns = [
    path(
        'tasks/<int:pk>/',
        TaskViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}),
        name='task-detail',
    ),
    path(
        'projects/<int:project_id>/tasks/',
        TaskViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='task-list-by-project',
    ),
]


