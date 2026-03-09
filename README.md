# Feedback

## Overview

| Property | Value |
|----------|-------|
| **Module ID** | `feedback` |
| **Version** | `1.0.0` |
| **Icon** | `star-outline` |
| **Dependencies** | `customers` |

## Dependencies

This module requires the following modules to be installed:

- `customers`

## Models

### `FeedbackForm`

A feedback form template that defines the type of feedback to collect.

| Field | Type | Details |
|-------|------|---------|
| `name` | CharField | max_length=255 |
| `description` | TextField | optional |
| `form_type` | CharField | max_length=20, choices: rating_5, nps_10, stars_5, thumbs, text_only |
| `trigger_type` | CharField | max_length=20, choices: manual, post_sale, post_appointment, post_ticket |
| `trigger_delay_hours` | IntegerField |  |
| `include_comment` | BooleanField |  |
| `is_active` | BooleanField |  |
| `thank_you_message` | TextField | optional |

**Properties:**

- `response_count`
- `form_type_display`
- `trigger_type_display`
- `max_score` — Return the maximum score for this form type.
- `min_score` — Return the minimum score for this form type.

### `FeedbackResponse`

A single feedback response submitted by a customer.

| Field | Type | Details |
|-------|------|---------|
| `form` | ForeignKey | → `feedback.FeedbackForm`, on_delete=CASCADE |
| `customer` | ForeignKey | → `customers.Customer`, on_delete=SET_NULL, optional |
| `score` | IntegerField | optional |
| `comment` | TextField | optional |
| `status` | CharField | max_length=20, choices: new, reviewed, actioned |
| `reviewed_by` | UUIDField | max_length=32, optional |
| `reviewed_at` | DateTimeField | optional |
| `staff_notes` | TextField | optional |
| `related_sale` | UUIDField | max_length=32, optional |
| `related_appointment` | UUIDField | max_length=32, optional |
| `related_ticket` | UUIDField | max_length=32, optional |

**Methods:**

- `mark_reviewed()` — Mark this response as reviewed.
- `mark_actioned()` — Mark this response as actioned.

**Properties:**

- `nps_category` — Return NPS category for NPS-type forms.
Promoter: 9-10, Passive: 7-8, Detractor: 0-6
- `is_positive` — Determine if this feedback is positive.
- For NPS (0-10): score >= 7
- For 5-scale (rating_5, stars_5): score >= 4
- For thumbs: score == 1
- `score_color` — Return CSS color class based on score and form type.
- `score_badge_color` — Return badge color class based on score and form type.
- `status_badge_color` — Return badge color for status.

### `FeedbackSettings`

Per-hub settings for the feedback module.
Uses get_or_create pattern for singleton-like behavior.

| Field | Type | Details |
|-------|------|---------|
| `auto_send_post_sale` | BooleanField |  |
| `auto_send_post_appointment` | BooleanField |  |
| `default_form` | ForeignKey | → `feedback.FeedbackForm`, on_delete=SET_NULL, optional |
| `minimum_days_between_requests` | IntegerField |  |

**Methods:**

- `get_for_hub()` — Get or create settings for a specific hub.

## Cross-Module Relationships

| From | Field | To | on_delete | Nullable |
|------|-------|----|-----------|----------|
| `FeedbackResponse` | `form` | `feedback.FeedbackForm` | CASCADE | No |
| `FeedbackResponse` | `customer` | `customers.Customer` | SET_NULL | Yes |
| `FeedbackSettings` | `default_form` | `feedback.FeedbackForm` | SET_NULL | Yes |

## URL Endpoints

Base path: `/m/feedback/`

| Path | Name | Method |
|------|------|--------|
| `(root)` | `dashboard` | GET |
| `responses/` | `responses` | GET |
| `forms/` | `forms` | GET |
| `feedback_forms/` | `feedback_forms_list` | GET |
| `feedback_forms/add/` | `feedback_form_add` | GET/POST |
| `feedback_forms/<uuid:pk>/edit/` | `feedback_form_edit` | GET |
| `feedback_forms/<uuid:pk>/delete/` | `feedback_form_delete` | GET/POST |
| `feedback_forms/<uuid:pk>/toggle/` | `feedback_form_toggle_status` | GET |
| `feedback_forms/bulk/` | `feedback_forms_bulk_action` | GET/POST |
| `feedback_responses/` | `feedback_responses_list` | GET |
| `feedback_responses/add/` | `feedback_response_add` | GET/POST |
| `feedback_responses/<uuid:pk>/edit/` | `feedback_response_edit` | GET |
| `feedback_responses/<uuid:pk>/delete/` | `feedback_response_delete` | GET/POST |
| `feedback_responses/bulk/` | `feedback_responses_bulk_action` | GET/POST |
| `settings/` | `settings` | GET |

## Permissions

| Permission | Description |
|------------|-------------|
| `feedback.view_response` | View Response |
| `feedback.add_response` | Add Response |
| `feedback.change_response` | Change Response |
| `feedback.delete_response` | Delete Response |
| `feedback.view_form` | View Form |
| `feedback.add_form` | Add Form |
| `feedback.change_form` | Change Form |
| `feedback.delete_form` | Delete Form |
| `feedback.manage_settings` | Manage Settings |

**Role assignments:**

- **admin**: All permissions
- **manager**: `add_form`, `add_response`, `change_form`, `change_response`, `view_form`, `view_response`
- **employee**: `add_response`, `view_form`, `view_response`

## Navigation

| View | Icon | ID | Fullpage |
|------|------|----|----------|
| Dashboard | `speedometer-outline` | `dashboard` | No |
| Responses | `chatbubbles-outline` | `responses` | No |
| Forms | `document-text-outline` | `forms` | No |
| Settings | `settings-outline` | `settings` | No |

## AI Tools

Tools available for the AI assistant:

### `list_feedback_forms`

List feedback forms.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `is_active` | boolean | No |  |
| `form_type` | string | No |  |

### `create_feedback_form`

Create a feedback form (e.g., NPS survey, post-sale rating).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes |  |
| `description` | string | No |  |
| `form_type` | string | Yes | rating_5, nps_10, stars_5, thumbs, text_only |
| `trigger_type` | string | No | manual, post_sale, post_appointment, post_ticket |
| `include_comment` | boolean | No |  |
| `thank_you_message` | string | No |  |

### `list_feedback_responses`

List feedback responses with filters.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `form_id` | string | No |  |
| `status` | string | No | new, reviewed, actioned |
| `limit` | integer | No |  |

### `get_feedback_summary`

Get feedback summary: average score, response count, breakdown.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `form_id` | string | No |  |

## File Structure

```
README.md
__init__.py
admin.py
ai_tools.py
apps.py
forms.py
locale/
  en/
    LC_MESSAGES/
      django.po
  es/
    LC_MESSAGES/
      django.po
migrations/
  0001_initial.py
  __init__.py
models.py
module.py
static/
  feedback/
    css/
      feedback.css
    js/
templates/
  feedback/
    pages/
      dashboard.html
      feedback_form_add.html
      feedback_form_edit.html
      feedback_forms.html
      feedback_response_add.html
      feedback_response_edit.html
      feedback_responses.html
      form_add.html
      form_edit.html
      forms_list.html
      index.html
      responses.html
      settings.html
    partials/
      dashboard_content.html
      feedback_form_add_content.html
      feedback_form_edit_content.html
      feedback_forms_content.html
      feedback_forms_list.html
      feedback_response_add_content.html
      feedback_response_edit_content.html
      feedback_responses_content.html
      feedback_responses_list.html
      form_add_content.html
      form_edit_content.html
      forms_content.html
      forms_list_items.html
      panel_feedback_form_add.html
      panel_feedback_form_edit.html
      panel_feedback_response_add.html
      panel_feedback_response_edit.html
      panel_form_add.html
      panel_form_edit.html
      response_detail.html
      responses_content.html
      responses_list.html
      settings_content.html
tests/
  __init__.py
  conftest.py
  test_models.py
  test_views.py
urls.py
views.py
```
