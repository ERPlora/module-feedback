"""
AI context for the Feedback module.
Loaded into the assistant system prompt when this module's tools are active.
"""

CONTEXT = """
## Module Knowledge: Feedback

### Models

**FeedbackForm** — A feedback form template defining how to collect feedback.
- `name`, `description`
- `form_type`: 'rating_5' (1-5) | 'nps_10' (0-10 NPS) | 'stars_5' (1-5 stars) | 'thumbs' (0/1) | 'text_only' (no score)
- `trigger_type`: 'manual' | 'post_sale' | 'post_appointment' | 'post_ticket'
- `trigger_delay_hours` (default 24): Hours to wait after event before sending
- `include_comment` (bool)
- `is_active`
- `thank_you_message`: Shown after submission
- Score range: nps_10 → 0-10; rating_5/stars_5 → 1-5; thumbs → 0 or 1; text_only → no score

**FeedbackResponse** — A single customer feedback submission.
- `form` FK → FeedbackForm (related_name='responses')
- `customer` FK → customers.Customer (nullable — anonymous allowed)
- `score` (IntegerField, nullable): Numeric score within the form's range
- `comment` (TextField)
- `status`: 'new' | 'reviewed' | 'actioned'
- `reviewed_by` (UUIDField), `reviewed_at`, `staff_notes`
- `related_sale` (UUIDField, optional), `related_appointment` (UUIDField, optional), `related_ticket` (UUIDField, optional)
- Properties:
  - `nps_category`: 'promoter' (9-10) | 'passive' (7-8) | 'detractor' (0-6) — only for nps_10
  - `is_positive`: True if score is in the "good" range (NPS≥7, stars≥4, thumbs=1)
- Methods: `mark_reviewed(reviewer_id)`, `mark_actioned(reviewer_id)`

**FeedbackSettings** — Per-hub configuration (singleton).
- `auto_send_post_sale` (bool), `auto_send_post_appointment` (bool)
- `default_form` FK → FeedbackForm
- `minimum_days_between_requests` (default 30): Throttle to avoid spamming customers
- Use `FeedbackSettings.get_for_hub(hub_id)`

### Key Flows

1. **Create form**: Create FeedbackForm with form_type and trigger_type
2. **Collect feedback**: Create FeedbackResponse (status='new') with score + optional comment; link to customer, sale, or appointment
3. **Review response**: `response.mark_reviewed(reviewer_id)` → status='reviewed'
4. **Action response**: `response.mark_actioned(reviewer_id)` → status='actioned' (implies follow-up done)
5. **Auto-trigger**: If trigger_type='post_sale' and auto_send_post_sale=True in settings, send feedback request after `trigger_delay_hours` following a sale

### Score Interpretation
| Form Type | Score Range | Positive Threshold |
|-----------|-------------|-------------------|
| nps_10    | 0-10        | ≥7 (passive), ≥9 (promoter) |
| rating_5  | 1-5         | ≥4 |
| stars_5   | 1-5         | ≥4 |
| thumbs    | 0 or 1      | = 1 |
| text_only | None        | N/A |

### Relationships
- `FeedbackResponse.customer` → customers.Customer
- `FeedbackResponse.related_sale` → UUID only (not FK)
"""
