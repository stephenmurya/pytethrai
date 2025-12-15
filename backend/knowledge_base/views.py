from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LibraryItem, Tag
from .serializers import LibraryItemSerializer, TagSerializer
from api.models import Message

class LibraryItemViewSet(viewsets.ModelViewSet):
    serializer_class = LibraryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = LibraryItem.objects.all()

        # 1. Always include private items owned by user
        # We will build a complex query using Q objects
        from django.db.models import Q
        
        # Base filter: Own items
        base_query = Q(user=user)

        # 2. Check for active workspace context
        workspace_id = self.request.query_params.get('workspace')
        
        if workspace_id:
            # Verify membership
            from teams.models import WorkspaceMember
            is_member = WorkspaceMember.objects.filter(workspace_id=workspace_id, user=user).exists()
            
            if is_member:
                # Include Workspace-visible items
                workspace_query = Q(workspace_id=workspace_id, visibility='WORKSPACE')
                
                # Include Subteam-visible items (if user is in that subteam)
                # First, get user's subteams in this workspace
                user_subteam_ids = user.subteams.filter(workspace_id=workspace_id).values_list('id', flat=True)
                subteam_query = Q(subteam_id__in=user_subteam_ids, visibility='SUBTEAM')
                
                # Combine
                final_query = base_query | workspace_query | subteam_query
                return queryset.filter(final_query).distinct().order_by('-created_at')

        # Default: Only return own items (Private or otherwise, but since we only see WORKSPACE items if workspace_id is set...)
        # Actually, if I created an item with visibility=WORKSPACE but I am viewing "My Library" (no workspace set), 
        # I should still see it because I own it.
        return queryset.filter(base_query).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='star')
    def toggle_star(self, request):
        message_id = request.data.get('message_id')
        if not message_id:
            return Response({"error": "message_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if item exists for this message
        existing_item = LibraryItem.objects.filter(
            user=request.user, 
            original_message_id=message_id
        ).first()

        if existing_item:
            existing_item.delete()
            return Response({"status": "removed", "message_id": message_id}, status=status.HTTP_200_OK)
        
        try:
            message = Message.objects.get(id=message_id) # Ensure message exists generally (global check?) or check if user has access? 
            # Note: Message model has chat with user. Ideally we should check if message.chat.user == request.user
            if message.chat.user != request.user:
                 return Response({"error": "Message not found or access denied"}, status=status.HTTP_404_NOT_FOUND)

            new_item = LibraryItem.objects.create(
                user=request.user,
                content=message.content,
                item_type='PROMPT',
                title=message.content[:50],
                original_message=message
            )
            serializer = self.get_serializer(new_item)
            return Response({"status": "created", "item": serializer.data}, status=status.HTTP_201_CREATED)

        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)

class TagViewSet(viewsets.ModelViewSet):
    # Optional: If we want to manage tags via API
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated]
