from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FeedbackConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'feedback'
    label = 'feedback'
    verbose_name = _('Feedback')

    def ready(self):
        pass
