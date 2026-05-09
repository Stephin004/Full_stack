from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    ADMIN = 'ADMIN'
    MEMBER = 'MEMBER'
    ROLE_CHOICES = [(ADMIN, 'Admin'), (MEMBER, 'Member')]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=MEMBER)

    class Meta:
        unique_together = ('user', 'project')

    def __str__(self):
        return f"{self.user_id} in {self.project_id} ({self.role})"

