# assessment/admin.py
from django.contrib import admin
from .models import Question, Choice, AssessmentResult
from django.utils.html import format_html
import json

class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'question_type', 'order')
    list_filter = ('question_type',)
    search_fields = ('question_text',)
    
    # The inline is always declared here
    inlines = [ChoiceInline]

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('get_user_name', 'created_at')
    readonly_fields = ('pretty_answers', 'created_at')
    exclude = ('answers',)

    def get_user_name(self, obj):
        """
        Safely reads the user's name from the answers JSON,
        handling cases where the data is a string or a dictionary.
        """
        answers_data = obj.answers
        # THE FIX: Check if the data is a string. If so, parse it.
        if isinstance(answers_data, str):
            try:
                answers_data = json.loads(answers_data)
            except json.JSONDecodeError:
                # Handle cases of corrupted data
                return 'Invalid JSON'
        
        # Now we can be sure answers_data is a dictionary
        return answers_data.get('user_name', 'N/A')
    
    get_user_name.short_description = 'User Name'

    def pretty_answers(self, instance):
        # This function also needs the same safety check
        answers_data = instance.answers
        if isinstance(answers_data, str):
            try:
                answers_data = json.loads(answers_data)
            except json.JSONDecodeError:
                return 'Invalid JSON'

        pretty_json = json.dumps(answers_data, indent=4, ensure_ascii=False)
        return format_html('<pre>{}</pre>', pretty_json)
    
    pretty_answers.short_description = 'User Answers'