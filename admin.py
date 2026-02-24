from django.contrib import admin

from .models import FeedbackForm, FeedbackResponse

@admin.register(FeedbackForm)
class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'form_type', 'trigger_type', 'trigger_delay_hours', 'created_at']
    search_fields = ['name', 'description', 'form_type', 'trigger_type']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'customer', 'score', 'status', 'created_at']
    search_fields = ['comment', 'status', 'staff_notes']
    readonly_fields = ['created_at', 'updated_at']

