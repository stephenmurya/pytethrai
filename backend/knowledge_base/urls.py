from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LibraryItemViewSet, TagViewSet

router = DefaultRouter()
router.register(r'library', LibraryItemViewSet, basename='library')
router.register(r'tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
