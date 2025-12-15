from django.db import models
from django.contrib.auth.models import User

class UsageLog(models.Model):
    # Nullable if tracked before we had workspaces, or for personal playground usage
    workspace = models.ForeignKey('teams.Workspace', on_delete=models.SET_NULL, null=True, blank=True, related_name='usage_logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_logs')
    model_name = models.CharField(max_length=50)
    input_tokens = models.IntegerField(default=0)
    output_tokens = models.IntegerField(default=0)
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.model_name} - ${self.cost_estimate}"
