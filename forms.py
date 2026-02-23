from django import forms
from django.utils.translation import gettext_lazy as _

from .models import FeedbackForm, FeedbackResponse, FeedbackSettings


class FeedbackFormForm(forms.ModelForm):
    """Form for creating/editing FeedbackForm instances."""

    class Meta:
        model = FeedbackForm
        fields = [
            'name', 'description', 'form_type', 'trigger_type',
            'trigger_delay_hours', 'include_comment', 'is_active',
            'thank_you_message',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'input',
                'placeholder': _('Form name'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 2,
                'placeholder': _('Description (optional)'),
            }),
            'form_type': forms.Select(attrs={
                'class': 'select',
            }),
            'trigger_type': forms.Select(attrs={
                'class': 'select',
            }),
            'trigger_delay_hours': forms.NumberInput(attrs={
                'class': 'input',
                'min': '0',
                'placeholder': '24',
            }),
            'include_comment': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'thank_you_message': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Thank you for your feedback!'),
            }),
        }


class FeedbackResponseForm(forms.ModelForm):
    """Form for editing feedback response staff notes."""

    class Meta:
        model = FeedbackResponse
        fields = ['staff_notes']
        widgets = {
            'staff_notes': forms.Textarea(attrs={
                'class': 'textarea',
                'rows': 3,
                'placeholder': _('Add staff notes...'),
            }),
        }


class FeedbackSettingsForm(forms.ModelForm):
    """Form for editing feedback module settings."""

    class Meta:
        model = FeedbackSettings
        fields = [
            'auto_send_post_sale', 'auto_send_post_appointment',
            'default_form', 'minimum_days_between_requests',
        ]
        widgets = {
            'auto_send_post_sale': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'auto_send_post_appointment': forms.CheckboxInput(attrs={
                'class': 'toggle',
            }),
            'default_form': forms.Select(attrs={
                'class': 'select',
            }),
            'minimum_days_between_requests': forms.NumberInput(attrs={
                'class': 'input',
                'min': '1',
                'placeholder': '30',
            }),
        }

    def __init__(self, *args, hub_id=None, **kwargs):
        super().__init__(*args, **kwargs)
        if hub_id:
            self.fields['default_form'].queryset = FeedbackForm.objects.filter(
                hub_id=hub_id, is_deleted=False, is_active=True,
            )
        self.fields['default_form'].required = False
        self.fields['default_form'].empty_label = _('-- No default form --')


class FeedbackResponseFilterForm(forms.Form):
    """Filter form for responses list."""

    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'input',
            'placeholder': _('Search by customer or comment...'),
        }),
    )
    form_filter = forms.ModelChoiceField(
        required=False,
        queryset=FeedbackForm.objects.none(),
        empty_label=_('All Forms'),
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', _('All Status')),
            ('new', _('New')),
            ('reviewed', _('Reviewed')),
            ('actioned', _('Actioned')),
        ],
        widget=forms.Select(attrs={
            'class': 'select',
        }),
    )
