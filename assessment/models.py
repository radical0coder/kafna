from django.db import models
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
import json

# This encoder is still needed for our JSONFields
class UnsafeJSONEncoder(DjangoJSONEncoder):
    def __init__(self, *args, **kwargs):
        kwargs['ensure_ascii'] = False
        super().__init__(*args, **kwargs)

# --- NEW MODELS ---

class Job(models.Model):
    """Represents a 'mother job' or career path."""
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Test(models.Model):
    """A container for a set of questions and its AI prompt."""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    
    # Stores the list of question objects as JSON
    questions = models.JSONField(encoder=UnsafeJSONEncoder)
    
    # The specific instructions for the AI for this test
    system_prompt = models.TextField()

    # Link to a job for level-measurement tests
    related_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Flag to identify the first test for all new users
    is_primary_assessment = models.BooleanField(default=False, help_text="Set to True for the one test all new users must take first.")
    
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

# --- UPGRADED MODEL ---

class AssessmentResult(models.Model):
    """Links a user to a specific test they have taken."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assessments")
    
    # NEW: Link to the specific Test that was taken
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="results")
    
    answers = models.JSONField(encoder=UnsafeJSONEncoder)
    ai_analysis = models.JSONField(encoder=UnsafeJSONEncoder, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Result for {self.user.phone_number} on test '{self.test.name}'"

# The old Question and Choice models should be deleted.