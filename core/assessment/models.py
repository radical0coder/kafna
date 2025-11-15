from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import json

# NEW: Custom encoder to preserve Persian characters
class UnsafeJSONEncoder(DjangoJSONEncoder):
    def __init__(self, *args, **kwargs):
        # Set ensure_ascii to False to allow non-ASCII characters
        kwargs['ensure_ascii'] = False
        super().__init__(*args, **kwargs)


class Question(models.Model):
    """
    Represents a single question in the assessment test.
    """
    QUESTION_TYPES = [
        ('multiple', 'Multiple Choice'),
        ('slider', 'Slider / Range'),
        ('text', 'Text Input'),
    ]

    question_text = models.CharField(max_length=500)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='multiple')
    order = models.PositiveIntegerField(default=0, help_text="Determines the order in which questions are displayed.")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}. {self.question_text}"

class Choice(models.Model):
    """
    Represents an option for a 'multiple' choice question.
    """
    # related_name='choices' allows us to get all choices for a question object
    # using question.choices.all()
    question = models.ForeignKey(Question, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)

    def __str__(self):
        return self.choice_text
    
    
class AssessmentResult(models.Model):
    user_name = models.CharField(max_length=100, blank=True)
    user_phone = models.CharField(max_length=20, blank=True)
    answers = models.JSONField()  # stores full list with question text
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} - {self.created_at}"