from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
import uuid

from .models import Workspace, WorkspaceMember, SubTeam
from .serializers import WorkspaceSerializer, SubTeamSerializer, WorkspaceMemberSerializer

class WorkspaceViewSet(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return workspaces where the user is a member
        return Workspace.objects.filter(members__user=self.request.user)

    def perform_create(self, serializer):
        # Generate slug from name if not provided
        name = serializer.validated_data.get('name')
        slug = slugify(name)
        # Handle duplicates simply for MVP
        original_slug = slug
        count = 1
        while Workspace.objects.filter(slug=slug).exists():
            slug = f"{original_slug}-{count}"
            count += 1
            
        workspace = serializer.save(owner=self.request.user, slug=slug)
        # Add creator as OWNER
        WorkspaceMember.objects.create(workspace=workspace, user=self.request.user, role='OWNER')

    @action(detail=False, methods=['post'])
    def join(self, request):
        token = request.data.get('token')
        if not token:
            return Response({"error": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            workspace = Workspace.objects.get(invite_token=token)
        except Workspace.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_404_NOT_FOUND)
            
        if WorkspaceMember.objects.filter(workspace=workspace, user=request.user).exists():
             return Response({"message": "Already a member", "workspace_id": workspace.id})

        WorkspaceMember.objects.create(workspace=workspace, user=request.user, role='MEMBER')
        return Response({"message": "Joined successfully", "workspace": WorkspaceSerializer(workspace).data})

    @action(detail=True, methods=['post'], url_path='regenerate-invite')
    def regenerate_invite(self, request, pk=None):
        workspace = self.get_object()
        # Check permissions
        membership = WorkspaceMember.objects.filter(workspace=workspace, user=request.user).first()
        if not membership or membership.role not in ['OWNER', 'ADMIN']:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
            
        workspace.invite_token = uuid.uuid4()
        workspace.save()
        return Response({"invite_token": workspace.invite_token})

class SubTeamViewSet(viewsets.ModelViewSet):
    serializer_class = SubTeamSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter subteams by workspaces user is in
        return SubTeam.objects.filter(workspace__members__user=self.request.user)

    def perform_create(self, serializer):
        # Ensure user is admin/owner of the workspace
        workspace = serializer.validated_data.get('workspace')
        membership = WorkspaceMember.objects.filter(workspace=workspace, user=self.request.user).first()
        if not membership or membership.role not in ['OWNER', 'ADMIN']:
             raise permissions.PermissionDenied("You must be an admin to create subteams.")
        serializer.save()
