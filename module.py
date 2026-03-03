from django.utils.translation import gettext_lazy as _

MODULE_ID = 'feedback'
MODULE_NAME = _('Feedback')
MODULE_VERSION = '1.0.0'
MODULE_ICON = 'star-outline'
MODULE_DESCRIPTION = _('Customer feedback, NPS scores and satisfaction surveys')
MODULE_AUTHOR = 'ERPlora'
MODULE_CATEGORY = 'customer_experience'

MENU = {
    'label': _('Feedback'),
    'icon': 'star-outline',
    'order': 65,
}

NAVIGATION = [
    {'label': _('Dashboard'), 'icon': 'speedometer-outline', 'id': 'dashboard'},
    {'label': _('Responses'), 'icon': 'chatbubbles-outline', 'id': 'responses'},
    {'label': _('Forms'), 'icon': 'document-text-outline', 'id': 'forms'},
    {'label': _('Settings'), 'icon': 'settings-outline', 'id': 'settings'},
]

DEPENDENCIES = ['customers']

PERMISSIONS = [
    'feedback.view_response',
    'feedback.add_response',
    'feedback.change_response',
    'feedback.delete_response',
    'feedback.view_form',
    'feedback.add_form',
    'feedback.change_form',
    'feedback.delete_form',
    'feedback.manage_settings',
]

ROLE_PERMISSIONS = {
    "admin": ["*"],
    "manager": [
        "add_form",
        "add_response",
        "change_form",
        "change_response",
        "view_form",
        "view_response",
    ],
    "employee": [
        "add_response",
        "view_form",
        "view_response",
    ],
}
