from django.db import models
from django.contrib.auth.models import User
from api.models import Message
# Late import to prevent circular dependency if using strings, but direct import is fine if apps are loaded
# Using string references for 'teams.Workspace' etc is safer.

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, blank=True, help_text="Hex code, e.g. #FFFFFF")

    def __str__(self):
        return self.name

class LibraryItem(models.Model):
    ITEM_TYPES = [
        ('PROMPT', 'Prompt'),
        ('TEMPLATE', 'Template'),
        ('CONVERSATION', 'Conversation'),
    ]

    VISIBILITY_CHOICES = [
        ('PRIVATE', 'Private'),
        ('WORKSPACE', 'Workspace'),
        ('SUBTEAM', 'Sub-team'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='library_items')
    title = models.CharField(max_length=255)
    content = models.TextField(help_text="Stores the prompt text or template content.")
    item_type = models.CharField(max_length=20, choices=ITEM_TYPES, default='PROMPT')
    variables = models.JSONField(default=list, blank=True, help_text="Extracted {{variables}} for Templates")
    original_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name='saved_items')
    tags = models.ManyToManyField(Tag, blank=True, related_name='items')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # New Fields
    workspace = models.ForeignKey('teams.Workspace', on_delete=models.CASCADE, null=True, blank=True, related_name='library_items')
    subteam = models.ForeignKey('teams.SubTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='library_items')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='PRIVATE')

    def __str__(self):
        return f"{self.title} ({self.get_item_type_display()})"
