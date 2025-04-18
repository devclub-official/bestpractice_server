from django.db import models

# Create your models here.

class GeneratedConfig(models.Model):
    """생성된 설정 파일 기록"""
    language = models.CharField(max_length=50)
    framework = models.CharField(max_length=50)
    features = models.JSONField()
    file_format = models.CharField(max_length=20)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.framework} config ({self.file_format}) - {self.created_at}"