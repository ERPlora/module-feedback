"""Tests for feedback models."""
import pytest
from django.utils import timezone

from feedback.models import FeedbackForm, FeedbackResponse


@pytest.mark.django_db
class TestFeedbackForm:
    """FeedbackForm model tests."""

    def test_create(self, feedback_form):
        """Test FeedbackForm creation."""
        assert feedback_form.pk is not None
        assert feedback_form.is_deleted is False

    def test_str(self, feedback_form):
        """Test string representation."""
        assert str(feedback_form) is not None
        assert len(str(feedback_form)) > 0

    def test_soft_delete(self, feedback_form):
        """Test soft delete."""
        pk = feedback_form.pk
        feedback_form.is_deleted = True
        feedback_form.deleted_at = timezone.now()
        feedback_form.save()
        assert not FeedbackForm.objects.filter(pk=pk).exists()
        assert FeedbackForm.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, feedback_form):
        """Test default queryset excludes deleted."""
        feedback_form.is_deleted = True
        feedback_form.deleted_at = timezone.now()
        feedback_form.save()
        assert FeedbackForm.objects.filter(hub_id=hub_id).count() == 0

    def test_toggle_active(self, feedback_form):
        """Test toggling is_active."""
        original = feedback_form.is_active
        feedback_form.is_active = not original
        feedback_form.save()
        feedback_form.refresh_from_db()
        assert feedback_form.is_active != original


@pytest.mark.django_db
class TestFeedbackResponse:
    """FeedbackResponse model tests."""

    def test_create(self, feedback_response):
        """Test FeedbackResponse creation."""
        assert feedback_response.pk is not None
        assert feedback_response.is_deleted is False

    def test_soft_delete(self, feedback_response):
        """Test soft delete."""
        pk = feedback_response.pk
        feedback_response.is_deleted = True
        feedback_response.deleted_at = timezone.now()
        feedback_response.save()
        assert not FeedbackResponse.objects.filter(pk=pk).exists()
        assert FeedbackResponse.all_objects.filter(pk=pk).exists()

    def test_queryset_excludes_deleted(self, hub_id, feedback_response):
        """Test default queryset excludes deleted."""
        feedback_response.is_deleted = True
        feedback_response.deleted_at = timezone.now()
        feedback_response.save()
        assert FeedbackResponse.objects.filter(hub_id=hub_id).count() == 0


