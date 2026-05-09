from django.db.models import Count
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task


class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localdate()

        # Tasks assigned to me grouped by status
        tasks_by_status = (
            Task.objects.filter(assignee=user)
            .values('status')
            .annotate(count=Count('id'))
            .order_by('status')
        )

        # Overdue tasks: due_date < today and status != DONE
        overdue_count = Task.objects.filter(
            assignee=user,
            due_date__lt=today,
        ).exclude(status=Task.DONE).count()

        # Active projects where I'm a member
        active_projects = user.memberships.values('project_id').distinct().count()

        # Task counts by status (same data, but explicit key for charts)
        task_status_counts = [
            {'status': row['status'], 'count': row['count']} for row in tasks_by_status
        ]

        return Response(
            {
                'active_projects': active_projects,
                'overdue_count': overdue_count,
                'tasks_assigned_to_me_by_status': task_status_counts,
                'task_counts_by_status': task_status_counts,
            }
        )

