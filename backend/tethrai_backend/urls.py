from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/knowledge/', include('knowledge_base.urls')),
    path('api/teams/', include('teams.urls')),
    path('api/analytics/', include('analytics.urls')),
]
