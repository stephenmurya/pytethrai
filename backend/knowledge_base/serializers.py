from rest_framework import serializers
from .models import Tag, LibraryItem

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color']

class LibraryItemSerializer(serializers.ModelSerializer):
    is_template = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        write_only=True, 
        queryset=Tag.objects.all(), 
        source='tags',
        required=False
    )

    class Meta:
        model = LibraryItem
        fields = [
            'id', 'user', 'title', 'content', 'item_type', 
            'variables', 'original_message', 'tags', 'tag_ids',
            'created_at', 'updated_at', 'is_template'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_is_template(self, obj):
        return obj.item_type == 'TEMPLATE'

    def create(self, validated_data):
        # Assign current user from context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
