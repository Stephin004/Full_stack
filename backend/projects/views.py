from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.models import User
from projects.models import Membership, Project


class IsProjectAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj if isinstance(obj, Project) else getattr(obj, 'project', None)
        if not project:
            return False
        return Membership.objects.filter(user=request.user, project=project, role=Membership.ADMIN).exists()


class IsProjectMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        project = obj if isinstance(obj, Project) else getattr(obj, 'project', None)
        if not project:
            return False
        return Membership.objects.filter(user=request.user, project=project).exists()


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()

    def get_serializer_class(self):
        # lightweight serializers inline to keep scaffolding moving
        return None

    def get_queryset(self):
        return Project.objects.filter(memberships__user=self.request.user).distinct()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            perms = [permissions.IsAuthenticated, IsProjectAdmin]
        else:
            perms = [permissions.IsAuthenticated, IsProjectMember]
        return perms

    def perform_create(self, serializer):
        project = serializer.save(owner=self.request.user)
        Membership.objects.create(user=self.request.user, project=project, role=Membership.ADMIN)

    def list(self, request, *args, **kwargs):
        data = []
        for p in self.get_queryset().order_by('-created_at'):
            role = Membership.objects.filter(user=request.user, project=p).values_list('role', flat=True).first()
            data.append({'id': p.id, 'name': p.name, 'description': p.description, 'role': role, 'created_at': p.created_at})
        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        if not Membership.objects.filter(user=request.user, project=project).exists():
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        members = Membership.objects.filter(project=project).select_related('user')
        member_list = [
            {'id': m.user.id, 'email': m.user.email, 'role': m.role, 'name': m.user.first_name}
            for m in members
        ]
        my_role = Membership.objects.get(user=request.user, project=project).role
        return Response(
            {
                'id': project.id,
                'name': project.name,
                'description': project.description,
                'my_role': my_role,
                'members': member_list,
                'created_at': project.created_at,
            }
        )

    def create(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response({'detail': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)
        name = request.data.get('name')
        description = request.data.get('description', '')
        if not name:
            return Response({'error': 'name is required', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
        project = Project.objects.create(name=name, description=description, owner=request.user)
        Membership.objects.create(user=request.user, project=project, role=Membership.ADMIN)
        return Response({'id': project.id, 'name': project.name, 'description': project.description}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        if not Membership.objects.filter(user=request.user, project=project, role=Membership.ADMIN).exists():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        if 'name' in request.data:
            project.name = request.data['name']
        if 'description' in request.data:
            project.description = request.data['description']
        project.save()
        return Response({'id': project.id, 'name': project.name, 'description': project.description})

    def destroy(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs['pk'])
        if not Membership.objects.filter(user=request.user, project=project, role=Membership.ADMIN).exists():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectMembersView(viewsets.ViewSet):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if not Membership.objects.filter(user=request.user, project=project, role=Membership.ADMIN).exists():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        role = request.data.get('role', Membership.MEMBER)
        if role not in [Membership.ADMIN, Membership.MEMBER]:
            return Response({'error': 'invalid role', 'details': {}}, status=status.HTTP_400_BAD_REQUEST)
        member = get_object_or_404(User, pk=user_id)
        Membership.objects.update_or_create(user=member, project=project, defaults={'role': role})
        return Response({'status': 'member added'})

    def delete(self, request, project_id, uid):
        project = get_object_or_404(Project, pk=project_id)
        if not Membership.objects.filter(user=request.user, project=project, role=Membership.ADMIN).exists():
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        Membership.objects.filter(user_id=uid, project=project).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

