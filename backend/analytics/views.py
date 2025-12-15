from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.utils import timezone
from datetime import timedelta
from .models import UsageLog
from teams.models import WorkspaceMember

class UsageDashboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        user = request.user
        workspace_id = request.query_params.get('workspace')
        
        # Base Query
        logs = UsageLog.objects.all()
        
        # Filter Logic
        if workspace_id:
            # Check permission
            if not WorkspaceMember.objects.filter(workspace_id=workspace_id, user=user).exists():
                 return Response({"error": "Permission denied"}, status=403)
            # Filter logs for this workspace
            logs = logs.filter(workspace_id=workspace_id)
        else:
            # Personal filtering (logs owned by user OR logs from personal usage where workspace is null)
            # Actually, standard behavior for "Personal View" usually means "My Usage across context" OR "My Personal Workspace Usage".
            # Let's define "Personal View" as: Logs where correct user is involved. 
            # If we want ONLY private usage, we filter workspace__isnull=True.
            # But the user might want "My Cost" across all teams?
            # Let's stick to "Personal Scope" = Logs where workspace is None.
            logs = logs.filter(user=user, workspace__isnull=True)

        # 1. Total Cost & Requests
        total_cost = logs.aggregate(Sum('cost_estimate'))['cost_estimate__sum'] or 0
        total_requests = logs.count()
        
        # 2. Usage by User (Relevant for Team view)
        usage_by_user = logs.values('user__username').annotate(
            total_cost=Sum('cost_estimate'),
            request_count=Count('id')
        ).order_by('-total_cost')
        
        # 3. Usage by Model
        usage_by_model = logs.values('model_name').annotate(
            total_cost=Sum('cost_estimate'),
            request_count=Count('id')
        ).order_by('-total_cost')
        
        # 4. Daily Usage (Last 30 Days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_usage = logs.filter(timestamp__gte=thirty_days_ago).annotate(
            date=TruncDay('timestamp')
        ).values('date').annotate(
            cost=Sum('cost_estimate'),
            requests=Count('id')
        ).order_by('date')
        
        return Response({
            "total_cost": total_cost,
            "total_requests": total_requests,
            "usage_by_user": usage_by_user,
            "usage_by_model": usage_by_model,
            "daily_usage": daily_usage
        })
