from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FeedbackForm, FeedbackResponse, FeedbackSettings

class FeedbackFormForm(forms.ModelForm):
    class Meta:
        model = FeedbackForm
        fields = ['name', 'description', 'form_type', 'trigger_type', 'trigger_delay_hours', 'include_comment', 'is_active', 'thank_you_message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'form_type': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'trigger_type': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'trigger_delay_hours': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'include_comment': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'thank_you_message': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
        }

class FeedbackResponseForm(forms.ModelForm):
    class Meta:
        model = FeedbackResponse
        fields = ['form', 'customer', 'score', 'comment', 'status', 'reviewed_by', 'reviewed_at', 'staff_notes', 'related_sale', 'related_appointment', 'related_ticket']
        widgets = {
            'form': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'customer': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'score': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
            'comment': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'reviewed_by': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'reviewed_at': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'datetime-local'}),
            'staff_notes': forms.Textarea(attrs={'class': 'textarea textarea-sm w-full', 'rows': 3}),
            'related_sale': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'related_appointment': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
            'related_ticket': forms.TextInput(attrs={'class': 'input input-sm w-full'}),
        }

class FeedbackSettingsForm(forms.ModelForm):
    class Meta:
        model = FeedbackSettings
        fields = ['auto_send_post_sale', 'auto_send_post_appointment', 'default_form', 'minimum_days_between_requests']
        widgets = {
            'auto_send_post_sale': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'auto_send_post_appointment': forms.CheckboxInput(attrs={'class': 'toggle'}),
            'default_form': forms.Select(attrs={'class': 'select select-sm w-full'}),
            'minimum_days_between_requests': forms.TextInput(attrs={'class': 'input input-sm w-full', 'type': 'number'}),
        }

