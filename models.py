import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.models.base import HubBaseModel


# ============================================================================
# Feedback Form
# ============================================================================

class FeedbackForm(HubBaseModel):
    """
    A feedback form template that defines the type of feedback to collect.
    """

    FORM_TYPE_CHOICES = [
        ('rating_5', _('1-5 Rating')),
        ('nps_10', _('NPS (0-10)')),
        ('stars_5', _('5 Stars')),
        ('thumbs', _('Thumbs Up/Down')),
        ('text_only', _('Text Only')),
    ]

    TRIGGER_TYPE_CHOICES = [
        ('manual', _('Manual')),
        ('post_sale', _('After Sale')),
        ('post_appointment', _('After Appointment')),
        ('post_ticket', _('After Support Ticket')),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Description'),
    )
    form_type = models.CharField(
        max_length=20,
        choices=FORM_TYPE_CHOICES,
        default='stars_5',
        verbose_name=_('Form Type'),
    )
    trigger_type = models.CharField(
        max_length=20,
        choices=TRIGGER_TYPE_CHOICES,
        default='manual',
        verbose_name=_('Trigger'),
    )
    trigger_delay_hours = models.IntegerField(
        default=24,
        verbose_name=_('Trigger Delay (hours)'),
        help_text=_('Hours to wait after the event before sending the feedback request'),
    )
    include_comment = models.BooleanField(
        default=True,
        verbose_name=_('Include Comment Field'),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_('Active'),
    )
    thank_you_message = models.TextField(
        blank=True,
        default='',
        verbose_name=_('Thank You Message'),
        help_text=_('Message shown after the customer submits feedback'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'feedback_feedbackform'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def response_count(self):
        return self.responses.filter(is_deleted=False).count()

    @property
    def form_type_display(self):
        return dict(self.FORM_TYPE_CHOICES).get(self.form_type, self.form_type)

    @property
    def trigger_type_display(self):
        return dict(self.TRIGGER_TYPE_CHOICES).get(self.trigger_type, self.trigger_type)

    @property
    def max_score(self):
        """Return the maximum score for this form type."""
        if self.form_type == 'nps_10':
            return 10
        elif self.form_type in ('rating_5', 'stars_5'):
            return 5
        elif self.form_type == 'thumbs':
            return 1
        return None

    @property
    def min_score(self):
        """Return the minimum score for this form type."""
        if self.form_type == 'nps_10':
            return 0
        elif self.form_type in ('rating_5', 'stars_5'):
            return 1
        elif self.form_type == 'thumbs':
            return 0
        return None


# ============================================================================
# Feedback Response
# ============================================================================

class FeedbackResponse(HubBaseModel):
    """
    A single feedback response submitted by a customer.
    """

    STATUS_CHOICES = [
        ('new', _('New')),
        ('reviewed', _('Reviewed')),
        ('actioned', _('Actioned')),
    ]

    form = models.ForeignKey(
        FeedbackForm,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Form'),
    )
    customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses',
        verbose_name=_('Customer'),
    )
    score = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Score'),
        help_text=_('Numeric score (0-10 for NPS, 1-5 for ratings, 0/1 for thumbs)'),
    )
    comment = models.TextField(
        blank=True,
        verbose_name=_('Comment'),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        db_index=True,
        verbose_name=_('Status'),
    )
    reviewed_by = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed By'),
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Reviewed At'),
    )
    staff_notes = models.TextField(
        blank=True,
        verbose_name=_('Staff Notes'),
    )

    # Related entities (optional UUIDs for cross-module references)
    related_sale = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Sale'),
    )
    related_appointment = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Appointment'),
    )
    related_ticket = models.UUIDField(
        null=True,
        blank=True,
        verbose_name=_('Related Ticket'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'feedback_feedbackresponse'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hub_id', 'status']),
            models.Index(fields=['hub_id', 'form']),
            models.Index(fields=['hub_id', 'customer']),
            models.Index(fields=['hub_id', 'created_at']),
        ]

    def __str__(self):
        customer_name = self.customer.name if self.customer else _('Anonymous')
        return f"{self.form.name} - {customer_name} ({self.score})"

    @property
    def nps_category(self):
        """
        Return NPS category for NPS-type forms.
        Promoter: 9-10, Passive: 7-8, Detractor: 0-6
        """
        if self.form.form_type != 'nps_10' or self.score is None:
            return None
        if self.score >= 9:
            return 'promoter'
        elif self.score >= 7:
            return 'passive'
        return 'detractor'

    @property
    def is_positive(self):
        """
        Determine if this feedback is positive.
        - For NPS (0-10): score >= 7
        - For 5-scale (rating_5, stars_5): score >= 4
        - For thumbs: score == 1
        """
        if self.score is None:
            return None
        form_type = self.form.form_type
        if form_type == 'nps_10':
            return self.score >= 7
        elif form_type in ('rating_5', 'stars_5'):
            return self.score >= 4
        elif form_type == 'thumbs':
            return self.score == 1
        return None

    @property
    def score_color(self):
        """Return CSS color class based on score and form type."""
        if self.score is None:
            return ''
        form_type = self.form.form_type
        if form_type == 'nps_10':
            if self.score >= 9:
                return 'text-success'
            elif self.score >= 7:
                return 'text-warning'
            return 'text-error'
        elif form_type in ('rating_5', 'stars_5'):
            if self.score >= 4:
                return 'text-success'
            elif self.score == 3:
                return 'text-warning'
            return 'text-error'
        elif form_type == 'thumbs':
            return 'text-success' if self.score == 1 else 'text-error'
        return ''

    @property
    def score_badge_color(self):
        """Return badge color class based on score and form type."""
        if self.score is None:
            return ''
        form_type = self.form.form_type
        if form_type == 'nps_10':
            if self.score >= 9:
                return 'color-success'
            elif self.score >= 7:
                return 'color-warning'
            return 'color-error'
        elif form_type in ('rating_5', 'stars_5'):
            if self.score >= 4:
                return 'color-success'
            elif self.score == 3:
                return 'color-warning'
            return 'color-error'
        elif form_type == 'thumbs':
            return 'color-success' if self.score == 1 else 'color-error'
        return ''

    @property
    def status_badge_color(self):
        """Return badge color for status."""
        colors = {
            'new': 'color-primary',
            'reviewed': 'color-warning',
            'actioned': 'color-success',
        }
        return colors.get(self.status, '')

    def mark_reviewed(self, reviewer_id=None):
        """Mark this response as reviewed."""
        self.status = 'reviewed'
        self.reviewed_by = reviewer_id
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])

    def mark_actioned(self, reviewer_id=None):
        """Mark this response as actioned."""
        self.status = 'actioned'
        if not self.reviewed_by:
            self.reviewed_by = reviewer_id
        if not self.reviewed_at:
            self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'updated_at'])


# ============================================================================
# Feedback Settings (singleton per hub)
# ============================================================================

class FeedbackSettings(HubBaseModel):
    """
    Per-hub settings for the feedback module.
    Uses get_or_create pattern for singleton-like behavior.
    """

    auto_send_post_sale = models.BooleanField(
        default=False,
        verbose_name=_('Auto-send after sale'),
        help_text=_('Automatically send feedback request after a completed sale'),
    )
    auto_send_post_appointment = models.BooleanField(
        default=False,
        verbose_name=_('Auto-send after appointment'),
        help_text=_('Automatically send feedback request after a completed appointment'),
    )
    default_form = models.ForeignKey(
        FeedbackForm,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name=_('Default Form'),
        help_text=_('Default feedback form to use when auto-sending'),
    )
    minimum_days_between_requests = models.IntegerField(
        default=30,
        verbose_name=_('Minimum days between requests'),
        help_text=_('Minimum number of days to wait before sending another feedback request to the same customer'),
    )

    class Meta(HubBaseModel.Meta):
        db_table = 'feedback_feedbacksettings'
        verbose_name = _('Feedback Settings')
        verbose_name_plural = _('Feedback Settings')

    def __str__(self):
        return _('Feedback Settings')

    @classmethod
    def get_for_hub(cls, hub_id):
        """Get or create settings for a specific hub."""
        obj, _ = cls.objects.get_or_create(hub_id=hub_id)
        return obj
