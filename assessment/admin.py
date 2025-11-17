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
    # THE FIX: We use the object's __str__ method for the display, which is clean.
    list_display = ('__str__', 'created_at', 'has_ai_analysis')
    readonly_fields = ('pretty_answers', 'pretty_ai_analysis', 'created_at', 'user' )
    exclude = ('answers', 'ai_analysis')

    def pretty_answers(self, instance):
        answers_data = instance.answers
        if isinstance(answers_data, str):
            try:
                answers_data = json.loads(answers_data)
            except json.JSONDecodeError:
                return 'Invalid JSON'
        pretty_json = json.dumps(answers_data, indent=4, ensure_ascii=False)
        return format_html(
            '<pre style="white-space: pre-wrap; word-wrap: break-word; max-width: 100%; overflow-x: auto;">{}</pre>',
            pretty_json
        )
    pretty_answers.short_description = 'User Answers'

    def pretty_ai_analysis(self, instance):
        if not instance.ai_analysis:
            return "No analysis generated."
        analysis_data = instance.ai_analysis
        if isinstance(analysis_data, str):
            try:
                analysis_data = json.loads(analysis_data)
            except json.JSONDecodeError:
                return 'Invalid JSON'
        pretty_json = json.dumps(analysis_data, indent=4, ensure_ascii=False)
        return format_html(
            '<pre style="white-space: pre-wrap; word-wrap: break-word; max-width: 100%; overflow-x: auto;">{}</pre>',
            pretty_json
        )
    pretty_ai_analysis.short_description = 'AI Analysis'

    def has_ai_analysis(self, obj):
        return bool(obj.ai_analysis)
    has_ai_analysis.boolean = True
    has_ai_analysis.short_description = 'Has Analysis'