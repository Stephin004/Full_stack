"""
URL configuration for config project.

For more information please see:
https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI / Swagger
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    # API
    path('api/', include('accounts.urls')),
    path('api/', include('projects.urls')),
    path('api/', include('tasks.urls')),
    path('api/', include('dashboard.urls')),
]

