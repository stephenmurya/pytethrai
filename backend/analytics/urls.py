from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsageDashboardViewSet

router = DefaultRouter()
# We use a custom basename because ViewSet doesn't use queryset directly in list
router.register(r'dashboard', UsageDashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
