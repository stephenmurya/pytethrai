from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Workspace, WorkspaceMember, SubTeam

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class WorkspaceMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = WorkspaceMember
        fields = ['id', 'user', 'role', 'joined_at']

class SubTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTeam
        fields = ['id', 'workspace', 'name', 'description', 'members']
        read_only_fields = ['workspace']

class WorkspaceSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    # Don't expose invite_token widely in list views if privacy matters, 
    # but for simplicity we allow it for members to invite others.
    
    class Meta:
        model = Workspace
        fields = ['id', 'name', 'slug', 'owner', 'invite_token', 'created_at']
