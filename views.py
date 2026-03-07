"""
Feedback Module Views
"""
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404, render as django_render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.accounts.decorators import login_required, permission_required
from apps.core.htmx import htmx_view
from apps.core.services import export_to_csv, export_to_excel
from apps.modules_runtime.navigation import with_module_nav

from .models import FeedbackForm, FeedbackResponse, FeedbackSettings

PER_PAGE_CHOICES = [10, 25, 50, 100]


# ======================================================================
# Dashboard
# ======================================================================

@login_required
@with_module_nav('feedback', 'dashboard')
@htmx_view('feedback/pages/index.html', 'feedback/partials/dashboard_content.html')
def dashboard(request):
    hub_id = request.session.get('hub_id')
    return {
        'total_feedback_forms': FeedbackForm.objects.filter(hub_id=hub_id, is_deleted=False).count(),
        'total_feedback_responses': FeedbackResponse.objects.filter(hub_id=hub_id, is_deleted=False).count(),
    }


# ======================================================================
# FeedbackForm
# ======================================================================

FEEDBACK_FORM_SORT_FIELDS = {
    'name': 'name',
    'form_type': 'form_type',
    'trigger_type': 'trigger_type',
    'include_comment': 'include_comment',
    'is_active': 'is_active',
    'trigger_delay_hours': 'trigger_delay_hours',
    'created_at': 'created_at',
}

def _build_feedback_forms_context(hub_id, per_page=10):
    qs = FeedbackForm.objects.filter(hub_id=hub_id, is_deleted=False).order_by('name')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'feedback_forms': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'name',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_feedback_forms_list(request, hub_id, per_page=10):
    ctx = _build_feedback_forms_context(hub_id, per_page)
    return django_render(request, 'feedback/partials/feedback_forms_list.html', ctx)

@login_required
@with_module_nav('feedback', 'responses')
@htmx_view('feedback/pages/feedback_forms.html', 'feedback/partials/feedback_forms_content.html')
def feedback_forms_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'name')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = FeedbackForm.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(form_type__icontains=search_query) | Q(trigger_type__icontains=search_query))

    order_by = FEEDBACK_FORM_SORT_FIELDS.get(sort_field, 'name')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['name', 'form_type', 'trigger_type', 'include_comment', 'is_active', 'trigger_delay_hours']
        headers = ['Name', 'Form Type', 'Trigger Type', 'Include Comment', 'Is Active', 'Trigger Delay Hours']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='feedback_forms.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='feedback_forms.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'feedback/partials/feedback_forms_list.html', {
            'feedback_forms': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'feedback_forms': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
@htmx_view('feedback/pages/feedback_form_add.html', 'feedback/partials/feedback_form_add_content.html')
def feedback_form_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        form_type = request.POST.get('form_type', '').strip()
        trigger_type = request.POST.get('trigger_type', '').strip()
        trigger_delay_hours = int(request.POST.get('trigger_delay_hours', 0) or 0)
        include_comment = request.POST.get('include_comment') == 'on'
        is_active = request.POST.get('is_active') == 'on'
        thank_you_message = request.POST.get('thank_you_message', '').strip()
        obj = FeedbackForm(hub_id=hub_id)
        obj.name = name
        obj.description = description
        obj.form_type = form_type
        obj.trigger_type = trigger_type
        obj.trigger_delay_hours = trigger_delay_hours
        obj.include_comment = include_comment
        obj.is_active = is_active
        obj.thank_you_message = thank_you_message
        obj.save()
        response = HttpResponse(status=204)
        response['HX-Redirect'] = reverse('feedback:feedback_forms_list')
        return response
    return {}

@login_required
@htmx_view('feedback/pages/feedback_form_edit.html', 'feedback/partials/feedback_form_edit_content.html')
def feedback_form_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(FeedbackForm, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.name = request.POST.get('name', '').strip()
        obj.description = request.POST.get('description', '').strip()
        obj.form_type = request.POST.get('form_type', '').strip()
        obj.trigger_type = request.POST.get('trigger_type', '').strip()
        obj.trigger_delay_hours = int(request.POST.get('trigger_delay_hours', 0) or 0)
        obj.include_comment = request.POST.get('include_comment') == 'on'
        obj.is_active = request.POST.get('is_active') == 'on'
        obj.thank_you_message = request.POST.get('thank_you_message', '').strip()
        obj.save()
        return _render_feedback_forms_list(request, hub_id)
    return {'obj': obj}

@login_required
@require_POST
def feedback_form_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(FeedbackForm, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_feedback_forms_list(request, hub_id)

@login_required
@require_POST
def feedback_form_toggle_status(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(FeedbackForm, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_active = not obj.is_active
    obj.save(update_fields=['is_active', 'updated_at'])
    return _render_feedback_forms_list(request, hub_id)

@login_required
@require_POST
def feedback_forms_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = FeedbackForm.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'activate':
        qs.update(is_active=True)
    elif action == 'deactivate':
        qs.update(is_active=False)
    elif action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_feedback_forms_list(request, hub_id)


# ======================================================================
# FeedbackResponse
# ======================================================================

FEEDBACK_RESPONSE_SORT_FIELDS = {
    'form': 'form',
    'customer': 'customer',
    'status': 'status',
    'score': 'score',
    'comment': 'comment',
    'reviewed_by': 'reviewed_by',
    'created_at': 'created_at',
}

def _build_feedback_responses_context(hub_id, per_page=10):
    qs = FeedbackResponse.objects.filter(hub_id=hub_id, is_deleted=False).order_by('form')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(1)
    return {
        'feedback_responses': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'form',
        'sort_dir': 'asc',
        'current_view': 'table',
        'per_page': per_page,
    }

def _render_feedback_responses_list(request, hub_id, per_page=10):
    ctx = _build_feedback_responses_context(hub_id, per_page)
    return django_render(request, 'feedback/partials/feedback_responses_list.html', ctx)

@login_required
@with_module_nav('feedback', 'responses')
@htmx_view('feedback/pages/feedback_responses.html', 'feedback/partials/feedback_responses_content.html')
def feedback_responses_list(request):
    hub_id = request.session.get('hub_id')
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'form')
    sort_dir = request.GET.get('dir', 'asc')
    page_number = request.GET.get('page', 1)
    current_view = request.GET.get('view', 'table')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    qs = FeedbackResponse.objects.filter(hub_id=hub_id, is_deleted=False)

    if search_query:
        qs = qs.filter(Q(comment__icontains=search_query) | Q(status__icontains=search_query) | Q(staff_notes__icontains=search_query))

    order_by = FEEDBACK_RESPONSE_SORT_FIELDS.get(sort_field, 'form')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    qs = qs.order_by(order_by)

    export_format = request.GET.get('export')
    if export_format in ('csv', 'excel'):
        fields = ['form', 'customer', 'status', 'score', 'comment', 'reviewed_by']
        headers = ["Name(id='FeedbackForm', ctx=Load())", 'customers.Customer', 'Status', 'Score', 'Comment', 'Reviewed By']
        if export_format == 'csv':
            return export_to_csv(qs, fields=fields, headers=headers, filename='feedback_responses.csv')
        return export_to_excel(qs, fields=fields, headers=headers, filename='feedback_responses.xlsx')

    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page_number)

    if request.htmx and request.htmx.target == 'datatable-body':
        return django_render(request, 'feedback/partials/feedback_responses_list.html', {
            'feedback_responses': page_obj, 'page_obj': page_obj,
            'search_query': search_query, 'sort_field': sort_field,
            'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
        })

    return {
        'feedback_responses': page_obj, 'page_obj': page_obj,
        'search_query': search_query, 'sort_field': sort_field,
        'sort_dir': sort_dir, 'current_view': current_view, 'per_page': per_page,
    }

@login_required
@htmx_view('feedback/pages/feedback_response_add.html', 'feedback/partials/feedback_response_add_content.html')
def feedback_response_add(request):
    hub_id = request.session.get('hub_id')
    if request.method == 'POST':
        score = int(request.POST.get('score', 0) or 0)
        comment = request.POST.get('comment', '').strip()
        status = request.POST.get('status', '').strip()
        reviewed_by = request.POST.get('reviewed_by', '').strip()
        reviewed_at = request.POST.get('reviewed_at') or None
        staff_notes = request.POST.get('staff_notes', '').strip()
        related_sale = request.POST.get('related_sale', '').strip()
        related_appointment = request.POST.get('related_appointment', '').strip()
        related_ticket = request.POST.get('related_ticket', '').strip()
        obj = FeedbackResponse(hub_id=hub_id)
        obj.score = score
        obj.comment = comment
        obj.status = status
        obj.reviewed_by = reviewed_by
        obj.reviewed_at = reviewed_at
        obj.staff_notes = staff_notes
        obj.related_sale = related_sale
        obj.related_appointment = related_appointment
        obj.related_ticket = related_ticket
        obj.save()
        return _render_feedback_responses_list(request, hub_id)
    return {}

@login_required
@htmx_view('feedback/pages/feedback_response_edit.html', 'feedback/partials/feedback_response_edit_content.html')
def feedback_response_edit(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(FeedbackResponse, pk=pk, hub_id=hub_id, is_deleted=False)
    if request.method == 'POST':
        obj.score = int(request.POST.get('score', 0) or 0)
        obj.comment = request.POST.get('comment', '').strip()
        obj.status = request.POST.get('status', '').strip()
        obj.reviewed_by = request.POST.get('reviewed_by', '').strip()
        obj.reviewed_at = request.POST.get('reviewed_at') or None
        obj.staff_notes = request.POST.get('staff_notes', '').strip()
        obj.related_sale = request.POST.get('related_sale', '').strip()
        obj.related_appointment = request.POST.get('related_appointment', '').strip()
        obj.related_ticket = request.POST.get('related_ticket', '').strip()
        obj.save()
        return _render_feedback_responses_list(request, hub_id)
    return {'obj': obj}

@login_required
@require_POST
def feedback_response_delete(request, pk):
    hub_id = request.session.get('hub_id')
    obj = get_object_or_404(FeedbackResponse, pk=pk, hub_id=hub_id, is_deleted=False)
    obj.is_deleted = True
    obj.deleted_at = timezone.now()
    obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])
    return _render_feedback_responses_list(request, hub_id)

@login_required
@require_POST
def feedback_responses_bulk_action(request):
    hub_id = request.session.get('hub_id')
    ids = [i.strip() for i in request.POST.get('ids', '').split(',') if i.strip()]
    action = request.POST.get('action', '')
    qs = FeedbackResponse.objects.filter(hub_id=hub_id, is_deleted=False, id__in=ids)
    if action == 'delete':
        qs.update(is_deleted=True, deleted_at=timezone.now())
    return _render_feedback_responses_list(request, hub_id)


# ======================================================================
# Settings
# ======================================================================

@login_required
@permission_required('feedback.manage_settings')
@with_module_nav('feedback', 'settings')
@htmx_view('feedback/pages/settings.html', 'feedback/partials/settings_content.html')
def settings_view(request):
    hub_id = request.session.get('hub_id')
    config, _ = FeedbackSettings.objects.get_or_create(hub_id=hub_id)
    if request.method == 'POST':
        config.auto_send_post_sale = request.POST.get('auto_send_post_sale') == 'on'
        config.auto_send_post_appointment = request.POST.get('auto_send_post_appointment') == 'on'
        config.default_form = request.POST.get('default_form', '').strip()
        config.minimum_days_between_requests = request.POST.get('minimum_days_between_requests', config.minimum_days_between_requests)
        config.save()
    return {'config': config}

