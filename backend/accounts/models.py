from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class UserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None  # type: ignore
    email = models.EmailField(unique=True)

    # Avoid clashes with auth.User reverse accessors when swapping AUTH_USER_MODEL
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='accounts_user_groups',
        related_query_name='accounts_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='accounts_user_permissions',
        related_query_name='accounts_user',
    )


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

