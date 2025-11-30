# assessment/admin.py
from django.contrib import admin
from .models import Job, Test, AssessmentResult
from django.utils.html import format_html
import json

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_primary_assessment', 'related_job', 'order')
    list_filter = ('is_primary_assessment', 'related_job')
    search_fields = ('name',)
    ordering = ('order',)

@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ('get_user_display', 'test', 'created_at', 'has_ai_analysis')
    list_filter = ('test', 'user')
    readonly_fields = ('user', 'test', 'pretty_answers', 'pretty_ai_analysis', 'created_at')
    exclude = ('answers', 'ai_analysis')

    def get_user_display(self, obj):
        user = obj.user
        full_name = user.get_full_name() if hasattr(user, 'get_full_name') else 'N/A'
        if full_name == '':
            full_name = getattr(user, 'full_name', 'N/A')
        phone = getattr(user, 'phone_number', '')
        return f"{phone} - {full_name}"
    get_user_display.short_description = 'User'

    def pretty_answers(self, instance):
        data = instance.answers
        pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre>{}</pre>', pretty)
    pretty_answers.short_description = 'User Answers'

    def pretty_ai_analysis(self, instance):
        data = instance.ai_analysis
        if not data: return "No analysis."
        pretty = json.dumps(data, indent=4, ensure_ascii=False)
        return format_html('<pre>{}</pre>', pretty)
    pretty_ai_analysis.short_description = 'AI Analysis'

    def has_ai_analysis(self, obj):
        return bool(obj.ai_analysis)
    has_ai_analysis.boolean = True
    has_ai_analysis.short_description = 'Has Analysis'