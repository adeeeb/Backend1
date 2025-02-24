from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.IntegerField()  # تغيير من CharField إلى IntegerField
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.user} - {self.session_id}"
