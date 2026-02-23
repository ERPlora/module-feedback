from django.urls import path
from . import views

app_name = 'feedback'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Responses
    path('responses/', views.responses_list, name='responses'),
    path('responses/<uuid:response_id>/', views.response_detail, name='response_detail'),
    path('responses/<uuid:response_id>/review/', views.response_review, name='response_review'),
    path('responses/<uuid:response_id>/delete/', views.response_delete, name='response_delete'),
    path('responses/bulk/', views.response_bulk_action, name='bulk_action'),

    # Forms
    path('forms/', views.forms_list, name='forms'),
    path('forms/add/', views.form_add, name='form_add'),
    path('forms/<uuid:form_id>/edit/', views.form_edit, name='form_edit'),
    path('forms/<uuid:form_id>/delete/', views.form_delete, name='form_delete'),
    path('forms/<uuid:form_id>/toggle/', views.form_toggle, name='form_toggle'),

    # Settings
    path('settings/', views.settings_view, name='settings'),
]
