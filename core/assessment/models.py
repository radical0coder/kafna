from django.db import models

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
    # This field determines how the question is rendered in the frontend.
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='multiple')
    # Use 'order' to control the sequence of questions.
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
    """
    Stores the answers submitted by a user for an assessment.
    """
    # In a real app, you would link this to a user with:
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    answers = models.JSONField() # Stores the answers object as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result submitted at {self.created_at.strftime('%Y-%m-%d %H:%M')}"