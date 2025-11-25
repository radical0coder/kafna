from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from assessment.models import AssessmentResult
from django.urls import reverse
from django.utils.html import format_html


class AssessmentResultInline(admin.TabularInline):
    model = AssessmentResult
    extra = 0
    # THE FIX: Add a new readonly_field that is a link
    fields = ('view_result_link', 'created_at')
    readonly_fields = ('view_result_link', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def view_result_link(self, obj):
        # This creates a link to the specific AssessmentResult admin page
        url = reverse('admin:assessment_assessmentresult_change', args=[obj.pk])
        return format_html('<a href="{}">View Full Result</a>', url)
    view_result_link.short_description = "Full Result"


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone_number', 'full_name', 'get_assessment_count', 'is_staff','is_premium')
    search_fields = ('phone_number',)
    list_filter = ('is_staff', 'is_superuser', 'is_active','is_premium', 'groups')
    inlines = [AssessmentResultInline]
    
    # This configures the fields shown when editing a user
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('full_name', 'address', 'age', 'about_me')}),
        ('Permissions', {'fields': ('is_active', 'is_staff','is_premium', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # This configures the fields shown when creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password'),
        }),
    )
    ordering = ('phone_number',)
    
    def get_assessment_count(self, obj):
        # This counts how many AssessmentResult objects are linked to this user
        return obj.assessments.count()
    get_assessment_count.short_description = 'Assessments Taken'