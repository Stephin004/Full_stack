from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from projects.models import Membership, Project
from tasks.models import Task


class TaskViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def _get_project(self, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if not Membership.objects.filter(user=self.request.user, project=project).exists():
            # Never leak existence: use 404 for non-member
            raise get_object_or_404(Project, pk=project_id, memberships__user=self.request.user)
        return project

    def list(self, request, project_id=None):
        project = self._get_project(project_id)
        tasks = Task.objects.filter(project=project).order_by('-created_at')
        return Response(
            [
                {
                    'id': t.id,
                    'title': t.title,
                    'description': t.description,
                    'assignee_id': t.assignee_id,
                    'status': t.status,
                    'priority': t.priority,
                    'due_date': t.due_date,
                    'created_at': t.created_at,
                }
                for t in tasks
            ]
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if not Membership.objects.filter(user=request.user, project=task.project).exists():
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'project_id': task.project_id,
                'assignee_id': task.assignee_id,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date,
                'created_at': task.created_at,
            }
        )

    def create(self, request, project_id=None):
        project = self._get_project(project_id)
        title = request.data.get('title')
        description = request.data.get('description', '')
        assignee_id = request.data.get('assignee_id')
        status_val = request.data.get('status', Task.TODO)
        priority = request.data.get('priority', 'MEDIUM')
        due_date = request.data.get('due_date')

        if not title:
            return Response({'error': 'title is required', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
        if status_val not in [Task.TODO, Task.IN_PROGRESS, Task.DONE]:
            return Response({'error': 'invalid status', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)

        assignee = None
        if assignee_id is not None:
            # assignee must be a member of the project
            if not Membership.objects.filter(user_id=assignee_id, project=project).exists():
                return Response({'error': 'assignee must be a project member', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
            assignee = Membership.objects.select_related('user').get(user_id=assignee_id, project=project).user

        if due_date:
            parsed = due_date
            # Expect ISO string; rely on DRF/date parsing later; for now block past date if parseable.
            try:
                due = timezone.datetime.fromisoformat(str(due_date)).date() if isinstance(due_date, str) else due_date
                if due < timezone.localdate():
                    return Response({'error': 'due_date cannot be in the past', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                pass

        task = Task.objects.create(
            title=title,
            description=description,
            project=project,
            assignee=assignee,
            status=status_val,
            priority=priority,
            due_date=due_date,
        )
        return Response({'id': task.id}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if not Membership.objects.filter(user=request.user, project=task.project).exists():
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Only Admins can reassign/delete; Members can update status of their own assigned tasks
        is_admin = Membership.objects.filter(user=request.user, project=task.project, role=Membership.ADMIN).exists()

        if not is_admin:
            # member can update only if task.assignee == request.user
            if task.assignee_id != request.user.id:
                return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            if 'status' in request.data:
                new_status = request.data.get('status')
                if new_status not in [Task.TODO, Task.IN_PROGRESS, Task.DONE]:
                    return Response({'error': 'invalid status', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
                task.status = new_status
                task.save(update_fields=['status'])
                return Response({'id': task.id, 'status': task.status})
            return Response({'error': 'Members can only update status of their own tasks', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)

        # Admin update (allow status, assignee, priority, due_date, title/description)
        for field in ['title', 'description', 'status', 'priority', 'due_date', 'assignee_id']:
            if field in request.data:
                if field == 'assignee_id':
                    assignee_id = request.data.get('assignee_id')
                    if assignee_id is not None and not Membership.objects.filter(user_id=assignee_id, project=task.project).exists():
                        return Response({'error': 'assignee must be a project member', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
                    task.assignee_id = assignee_id
                else:
                    setattr(task, field if field != 'assignee_id' else 'assignee', request.data.get(field))

        task.save()
        return Response({'id': task.id})

    def destroy(self, request, pk=None, *args, **kwargs):
        task = get_object_or_404(Task, pk=pk)
        if not Membership.objects.filter(user=request.user, project=task.project).exists():
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        is_admin = Membership.objects.filter(user=request.user, project=task.project, role=Membership.ADMIN).exists()
        if not is_admin:
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

