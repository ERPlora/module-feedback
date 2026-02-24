"""Tests for feedback views."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboard:
    """Dashboard view tests."""

    def test_dashboard_loads(self, auth_client):
        """Test dashboard page loads."""
        url = reverse('feedback:dashboard')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_dashboard_htmx(self, auth_client):
        """Test dashboard HTMX partial."""
        url = reverse('feedback:dashboard')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication."""
        url = reverse('feedback:dashboard')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestFeedbackFormViews:
    """FeedbackForm view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('feedback:feedback_forms_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('feedback:feedback_form_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('feedback:feedback_form_add')
        data = {
            'name': 'New Name',
            'description': 'Test description',
            'form_type': 'New Form Type',
            'trigger_type': 'New Trigger Type',
            'trigger_delay_hours': '5',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, feedback_form):
        """Test edit form loads."""
        url = reverse('feedback:feedback_form_edit', args=[feedback_form.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, feedback_form):
        """Test editing via POST."""
        url = reverse('feedback:feedback_form_edit', args=[feedback_form.pk])
        data = {
            'name': 'Updated Name',
            'description': 'Test description',
            'form_type': 'Updated Form Type',
            'trigger_type': 'Updated Trigger Type',
            'trigger_delay_hours': '5',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, feedback_form):
        """Test soft delete via POST."""
        url = reverse('feedback:feedback_form_delete', args=[feedback_form.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        feedback_form.refresh_from_db()
        assert feedback_form.is_deleted is True

    def test_toggle_status(self, auth_client, feedback_form):
        """Test toggle active status."""
        url = reverse('feedback:feedback_form_toggle_status', args=[feedback_form.pk])
        original = feedback_form.is_active
        response = auth_client.post(url)
        assert response.status_code == 200
        feedback_form.refresh_from_db()
        assert feedback_form.is_active != original

    def test_bulk_delete(self, auth_client, feedback_form):
        """Test bulk delete."""
        url = reverse('feedback:feedback_forms_bulk_action')
        response = auth_client.post(url, {'ids': str(feedback_form.pk), 'action': 'delete'})
        assert response.status_code == 200
        feedback_form.refresh_from_db()
        assert feedback_form.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('feedback:feedback_forms_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestFeedbackResponseViews:
    """FeedbackResponse view tests."""

    def test_list_loads(self, auth_client):
        """Test list view loads."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_list_htmx(self, auth_client):
        """Test list HTMX partial."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url, HTTP_HX_REQUEST='true')
        assert response.status_code == 200

    def test_list_search(self, auth_client):
        """Test list search."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url, {'q': 'test'})
        assert response.status_code == 200

    def test_list_sort(self, auth_client):
        """Test list sorting."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url, {'sort': 'created_at', 'dir': 'desc'})
        assert response.status_code == 200

    def test_export_csv(self, auth_client):
        """Test CSV export."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url, {'export': 'csv'})
        assert response.status_code == 200
        assert 'text/csv' in response['Content-Type']

    def test_export_excel(self, auth_client):
        """Test Excel export."""
        url = reverse('feedback:feedback_responses_list')
        response = auth_client.get(url, {'export': 'excel'})
        assert response.status_code == 200

    def test_add_form_loads(self, auth_client):
        """Test add form loads."""
        url = reverse('feedback:feedback_response_add')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_add_post(self, auth_client):
        """Test creating via POST."""
        url = reverse('feedback:feedback_response_add')
        data = {
            'score': '5',
            'comment': 'Test description',
            'status': 'New Status',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_edit_form_loads(self, auth_client, feedback_response):
        """Test edit form loads."""
        url = reverse('feedback:feedback_response_edit', args=[feedback_response.pk])
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_edit_post(self, auth_client, feedback_response):
        """Test editing via POST."""
        url = reverse('feedback:feedback_response_edit', args=[feedback_response.pk])
        data = {
            'score': '5',
            'comment': 'Test description',
            'status': 'Updated Status',
        }
        response = auth_client.post(url, data)
        assert response.status_code == 200

    def test_delete(self, auth_client, feedback_response):
        """Test soft delete via POST."""
        url = reverse('feedback:feedback_response_delete', args=[feedback_response.pk])
        response = auth_client.post(url)
        assert response.status_code == 200
        feedback_response.refresh_from_db()
        assert feedback_response.is_deleted is True

    def test_bulk_delete(self, auth_client, feedback_response):
        """Test bulk delete."""
        url = reverse('feedback:feedback_responses_bulk_action')
        response = auth_client.post(url, {'ids': str(feedback_response.pk), 'action': 'delete'})
        assert response.status_code == 200
        feedback_response.refresh_from_db()
        assert feedback_response.is_deleted is True

    def test_list_requires_auth(self, client):
        """Test list requires authentication."""
        url = reverse('feedback:feedback_responses_list')
        response = client.get(url)
        assert response.status_code == 302


@pytest.mark.django_db
class TestSettings:
    """Settings view tests."""

    def test_settings_loads(self, auth_client):
        """Test settings page loads."""
        url = reverse('feedback:settings')
        response = auth_client.get(url)
        assert response.status_code == 200

    def test_settings_requires_auth(self, client):
        """Test settings requires authentication."""
        url = reverse('feedback:settings')
        response = client.get(url)
        assert response.status_code == 302

