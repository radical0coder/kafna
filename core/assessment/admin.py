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
    list_display = ('user_name', 'user_phone', 'created_at', 'answers_summary')
    list_filter = ('created_at',)
    search_fields = ('user_name', 'user_phone', 'answers__question', 'answers__answer')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

    def answers_summary(self, obj):
        """
        Show a clean preview of answers in admin list view.
        Uses format_html() for safe HTML rendering.
        """
        if not obj.answers or not isinstance(obj.answers, list):
            return "—"

        # Limit to first 3 answers
        items = obj.answers[:3]
        lines = []

        for item in items:
            question = (item.get('question') or '')[:60]  # truncate long text
            answer = str(item.get('answer') or '—')
            lines.append(f"{question} → {answer}")

        summary = "<br>".join(lines)

        # Add "..." if more answers exist
        if len(obj.answers) > 3:
            summary += f"<br><em>... و {len(obj.answers) - 3} مورد دیگر</em>"

        # Use format_html for safe HTML
        return format_html(summary)

    answers_summary.short_description = "پاسخ‌ها"
    answers_summary.admin_order_field = 'created_at'  # optional sorting