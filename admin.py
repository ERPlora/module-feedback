from django.contrib import admin

from .models import FeedbackForm, FeedbackResponse, FeedbackSettings


@admin.register(FeedbackForm)
class FeedbackFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'form_type', 'trigger_type', 'is_active', 'created_at']
    list_filter = ['form_type', 'trigger_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'hub_id', 'created_at', 'updated_at']


@admin.register(FeedbackResponse)
class FeedbackResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'customer', 'score', 'status', 'created_at']
    list_filter = ['status', 'form']
    search_fields = ['comment', 'staff_notes']
    readonly_fields = ['id', 'hub_id', 'created_at', 'updated_at']
    raw_id_fields = ['form', 'customer']


@admin.register(FeedbackSettings)
class FeedbackSettingsAdmin(admin.ModelAdmin):
    list_display = ['hub_id', 'auto_send_post_sale', 'auto_send_post_appointment']
    readonly_fields = ['id', 'hub_id', 'created_at', 'updated_at']
