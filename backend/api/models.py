from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Transcript(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transcripts')
    video_id = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    content = models.TextField()
    language = models.CharField(max_length=10, default='hi')  # 'hi' for Hindi
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_favorite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['video_id']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'is_favorite']),
        ]
        unique_together = ['user', 'video_id']  # Prevent duplicate video_id per user

    def __str__(self):
        return f"{self.title} ({self.video_id})"

class Question(models.Model):
    QUESTION_TYPES = [
        ('novice', 'Novice'),
        ('mcq', 'Multiple Choice'),
        ('fill_blanks', 'Fill in the Blanks'),
    ]

    transcript = models.ForeignKey(Transcript, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    question_text = models.TextField()
    answer = models.TextField()
    options = models.JSONField(null=True, blank=True)  # For MCQ questions
    created_at = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    attempts = models.IntegerField(default=0)  # Track total attempts
    correct_attempts = models.IntegerField(default=0)  # Track correct attempts

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transcript', 'question_type']),
            models.Index(fields=['transcript', 'is_favorite']),
        ]

    def __str__(self):
        return f"{self.question_type} question for {self.transcript.title}"
