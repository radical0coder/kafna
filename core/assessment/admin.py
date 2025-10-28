from django.contrib import admin
from .models import Question, Choice, AssessmentResult
from django.utils.html import format_html
import json

class ChoiceInline(admin.TabularInline):
    """
    Allows admin to add and edit choices directly on the question page.
    """
    model = Choice
    extra = 3 # Show 3 extra empty choice forms by default

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'order')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
    
    # Add the ChoiceInline to the Question admin page
    inlines = [ChoiceInline]

    # A simple form enhancement to hide the choice inline for non-multiple-choice questions
    class Media:
        js = ('admin/js/question_admin.js',)
        
@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
    readonly_fields = ('pretty_answers', 'created_at') # Use the new pretty field
    exclude = ('answers',) # Hide the ugly raw field

    def pretty_answers(self, instance):
        # Convert the JSON object to a formatted HTML string
        pretty_json = json.dumps(instance.answers, indent=4, ensure_ascii=False)
        return format_html('<pre>{}</pre>', pretty_json)
    
    pretty_answers.short_description = 'User Answers'