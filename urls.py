from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # FeedbackForm
    path('feedback_forms/', views.feedback_forms_list, name='feedback_forms_list'),
    path('feedback_forms/add/', views.feedback_form_add, name='feedback_form_add'),
    path('feedback_forms/<uuid:pk>/edit/', views.feedback_form_edit, name='feedback_form_edit'),
    path('feedback_forms/<uuid:pk>/delete/', views.feedback_form_delete, name='feedback_form_delete'),
    path('feedback_forms/<uuid:pk>/toggle/', views.feedback_form_toggle_status, name='feedback_form_toggle_status'),
    path('feedback_forms/bulk/', views.feedback_forms_bulk_action, name='feedback_forms_bulk_action'),

    # FeedbackResponse
    path('feedback_responses/', views.feedback_responses_list, name='feedback_responses_list'),
    path('feedback_responses/add/', views.feedback_response_add, name='feedback_response_add'),
    path('feedback_responses/<uuid:pk>/edit/', views.feedback_response_edit, name='feedback_response_edit'),
    path('feedback_responses/<uuid:pk>/delete/', views.feedback_response_delete, name='feedback_response_delete'),
    path('feedback_responses/bulk/', views.feedback_responses_bulk_action, name='feedback_responses_bulk_action'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
