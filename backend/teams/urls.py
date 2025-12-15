from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkspaceViewSet, SubTeamViewSet

router = DefaultRouter()
router.register(r'workspaces', WorkspaceViewSet, basename='workspace')
router.register(r'subteams', SubTeamViewSet, basename='subteam')

urlpatterns = [
    path('', include(router.urls)),
]
