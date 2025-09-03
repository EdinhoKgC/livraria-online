from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PythonCommandLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    command = models.TextField()
    output = models.TextField()
    error = models.TextField(blank=True)
    execution_time = models.FloatField()  # em segundos
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.user.email} - {self.command[:50]} - {self.timestamp}"

