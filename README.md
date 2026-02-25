# Feedback Module

Customer feedback, NPS scores, and satisfaction surveys.

## Features

- Create customizable feedback forms with multiple types: 1-5 rating, NPS (0-10), 5 stars, thumbs up/down, and text only
- Configurable trigger types for automated feedback collection: manual, after sale, after appointment, after support ticket
- Trigger delay configuration (hours to wait before sending request)
- Optional comment field and custom thank-you messages per form
- Collect and manage feedback responses linked to customers
- NPS categorization (promoter, passive, detractor) for NPS-type forms
- Automatic positive/negative classification based on score and form type
- Response status workflow: new, reviewed, actioned
- Staff notes and review tracking on responses
- Cross-module references to related sales, appointments, and support tickets
- Per-hub settings for auto-send behavior and minimum days between requests
- Dashboard with feedback analytics and overview

## Installation

This module is installed automatically via the ERPlora Marketplace.

**Dependencies**: Requires `customers` module.

## Configuration

Access settings via: **Menu > Feedback > Settings**

Configurable options include:
- Auto-send feedback requests after sales or appointments
- Default feedback form for auto-sending
- Minimum days between requests to the same customer

## Usage

Access via: **Menu > Feedback**

### Views

| View | URL | Description |
|------|-----|-------------|
| Dashboard | `/m/feedback/dashboard/` | Overview of feedback metrics, scores, and trends |
| Responses | `/m/feedback/responses/` | View and manage submitted feedback responses |
| Forms | `/m/feedback/forms/` | Create and manage feedback form templates |
| Settings | `/m/feedback/settings/` | Configure feedback module settings |

## Models

| Model | Description |
|-------|-------------|
| `FeedbackForm` | Feedback form template defining type (rating, NPS, stars, thumbs, text), trigger, and display settings |
| `FeedbackResponse` | Individual feedback submission with score, comment, customer link, status, and staff review notes |
| `FeedbackSettings` | Per-hub singleton settings for auto-send behavior and request frequency |

## Permissions

| Permission | Description |
|------------|-------------|
| `feedback.view_response` | View feedback responses |
| `feedback.add_response` | Create feedback responses |
| `feedback.change_response` | Edit feedback responses |
| `feedback.delete_response` | Delete feedback responses |
| `feedback.view_form` | View feedback forms |
| `feedback.add_form` | Create feedback forms |
| `feedback.change_form` | Edit feedback forms |
| `feedback.delete_form` | Delete feedback forms |
| `feedback.manage_settings` | Manage feedback module settings |

## Integration with Other Modules

- **customers**: Feedback responses are linked to customer records via a foreign key. The customers module is required.

## License

MIT

## Author

ERPlora Team - support@erplora.com
