from django.db import models
from django.contrib.auth.models import User

class Transcript(models.Model):
    youtube_url = models.URLField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    language = models.CharField(max_length=10, default='hi')  # Default to Hindi
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.TextField()
    options = models.JSONField()  # Store multiple choice options
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.question_text

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'transcript')

    def __str__(self):
        return f"{self.user.username} - {self.transcript.title}"
