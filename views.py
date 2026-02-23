"""
Feedback Module Views

Dashboard, responses, forms, and settings management.
"""
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Case, When, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render as django_render
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.accounts.decorators import login_required
from apps.core.htmx import htmx_view
from apps.modules_runtime.navigation import with_module_nav

from .models import FeedbackForm, FeedbackResponse, FeedbackSettings


# ============================================================================
# Constants
# ============================================================================

RESPONSE_SORT_FIELDS = {
    'date': 'created_at',
    'score': 'score',
    'status': 'status',
    'customer': 'customer__name',
}

PER_PAGE_CHOICES = [10, 25, 50, 100]


def _hub_id(request):
    return request.session.get('hub_id')


def _user_id(request):
    return request.session.get('local_user_id')


def _render_responses_list(request, hub_id, per_page=10):
    """Render the responses list partial after a mutation."""
    responses = FeedbackResponse.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).select_related('form', 'customer').order_by('-created_at')
    paginator = Paginator(responses, per_page)
    page_obj = paginator.get_page(1)
    forms_list = FeedbackForm.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).order_by('name')
    return django_render(request, 'feedback/partials/responses_list.html', {
        'responses': page_obj,
        'page_obj': page_obj,
        'search_query': '',
        'sort_field': 'date',
        'sort_dir': 'desc',
        'form_filter': '',
        'status_filter': '',
        'forms_list': forms_list,
        'per_page': per_page,
    })


def _render_forms_list_items(request, hub_id):
    """Render the forms list partial after a mutation."""
    feedback_forms = FeedbackForm.objects.filter(
        hub_id=hub_id, is_deleted=False,
    ).annotate(
        total_responses=Count(
            'responses',
            filter=Q(responses__is_deleted=False),
        ),
    ).order_by('-created_at')
    return django_render(request, 'feedback/partials/forms_list_items.html', {
        'feedback_forms': feedback_forms,
    })


def _calculate_nps(responses_qs):
    """
    Calculate NPS score from a queryset of FeedbackResponse.
    Only considers NPS-type form responses.
    Returns: NPS score (int) or None if no data.
    """
    nps_responses = responses_qs.filter(
        form__form_type='nps_10',
        score__isnull=False,
    )
    total = nps_responses.count()
    if total == 0:
        return None

    promoters = nps_responses.filter(score__gte=9).count()
    detractors = nps_responses.filter(score__lte=6).count()

    nps = round(((promoters - detractors) / total) * 100)
    return nps


def _calculate_avg_rating(responses_qs):
    """
    Calculate average rating from 5-scale responses.
    Returns: average (float) or None.
    """
    rating_responses = responses_qs.filter(
        form__form_type__in=['rating_5', 'stars_5'],
        score__isnull=False,
    )
    result = rating_responses.aggregate(avg=Avg('score'))
    return round(result['avg'], 1) if result['avg'] is not None else None


# ============================================================================
# Dashboard
# ============================================================================

@login_required
@with_module_nav('feedback', 'dashboard')
@htmx_view('feedback/pages/dashboard.html', 'feedback/partials/dashboard_content.html')
def dashboard(request):
    """Feedback dashboard with NPS score, average rating, response count, trends."""
    hub = _hub_id(request)
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    all_responses = FeedbackResponse.objects.filter(
        hub_id=hub, is_deleted=False,
    )
    month_responses = all_responses.filter(created_at__gte=month_start)

    # NPS Score
    nps_score = _calculate_nps(all_responses)

    # Average Rating (all time)
    avg_rating = _calculate_avg_rating(all_responses)

    # Total responses this month
    total_this_month = month_responses.count()

    # Total responses all time
    total_all_time = all_responses.count()

    # Positive vs Negative for 5-scale ratings
    rating_responses = all_responses.filter(
        form__form_type__in=['rating_5', 'stars_5'],
        score__isnull=False,
    )
    positive_count = rating_responses.filter(score__gte=4).count()
    negative_count = rating_responses.filter(score__lte=2).count()
    neutral_count = rating_responses.filter(score=3).count()

    # NPS breakdown
    nps_responses = all_responses.filter(
        form__form_type='nps_10',
        score__isnull=False,
    )
    nps_total = nps_responses.count()
    nps_promoters = nps_responses.filter(score__gte=9).count()
    nps_passives = nps_responses.filter(score__gte=7, score__lte=8).count()
    nps_detractors = nps_responses.filter(score__lte=6).count()

    # Rating distribution (for 5-scale)
    rating_dist = []
    for i in range(1, 6):
        count = rating_responses.filter(score=i).count()
        rating_dist.append({
            'score': i,
            'count': count,
            'percent': round((count / rating_responses.count()) * 100) if rating_responses.count() > 0 else 0,
        })

    # NPS trend (last 6 months)
    nps_trend = []
    for i in range(5, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        month_label = timezone.datetime(y, m, 1).strftime('%b')
        month_end = timezone.datetime(
            y + (1 if m == 12 else 0),
            (m % 12) + 1,
            1,
            tzinfo=now.tzinfo,
        )
        month_begin = timezone.datetime(y, m, 1, tzinfo=now.tzinfo)
        month_nps_qs = all_responses.filter(
            created_at__gte=month_begin,
            created_at__lt=month_end,
        )
        month_nps = _calculate_nps(month_nps_qs)
        nps_trend.append({
            'month': month_label,
            'nps': month_nps if month_nps is not None else 0,
            'has_data': month_nps is not None,
        })

    # New responses count (new status)
    new_count = all_responses.filter(status='new').count()

    # Recent responses (last 10)
    recent_responses = all_responses.select_related(
        'form', 'customer',
    ).order_by('-created_at')[:10]

    # Response rate (responses with score vs total)
    scored_responses = all_responses.filter(score__isnull=False).count()
    response_rate = round((scored_responses / total_all_time) * 100) if total_all_time > 0 else 0

    return {
        'nps_score': nps_score,
        'avg_rating': avg_rating,
        'total_this_month': total_this_month,
        'total_all_time': total_all_time,
        'positive_count': positive_count,
        'negative_count': negative_count,
        'neutral_count': neutral_count,
        'nps_total': nps_total,
        'nps_promoters': nps_promoters,
        'nps_passives': nps_passives,
        'nps_detractors': nps_detractors,
        'rating_dist': rating_dist,
        'nps_trend': nps_trend,
        'new_count': new_count,
        'recent_responses': recent_responses,
        'response_rate': response_rate,
    }


# ============================================================================
# Responses List (Datatable)
# ============================================================================

@login_required
@with_module_nav('feedback', 'responses')
@htmx_view('feedback/pages/responses.html', 'feedback/partials/responses_content.html')
def responses_list(request):
    """Responses list with search, sort, filter, pagination."""
    hub = _hub_id(request)
    search_query = request.GET.get('q', '').strip()
    sort_field = request.GET.get('sort', 'date')
    sort_dir = request.GET.get('dir', 'desc')
    form_filter = request.GET.get('form', '')
    status_filter = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 10))
    if per_page not in PER_PAGE_CHOICES:
        per_page = 10

    responses = FeedbackResponse.objects.filter(
        hub_id=hub, is_deleted=False,
    ).select_related('form', 'customer')

    # Status filter
    if status_filter:
        responses = responses.filter(status=status_filter)

    # Form filter
    if form_filter:
        responses = responses.filter(form_id=form_filter)

    # Search
    if search_query:
        responses = responses.filter(
            Q(customer__name__icontains=search_query) |
            Q(comment__icontains=search_query) |
            Q(staff_notes__icontains=search_query)
        )

    # Sort
    order_by = RESPONSE_SORT_FIELDS.get(sort_field, 'created_at')
    if sort_dir == 'desc':
        order_by = f'-{order_by}'
    responses = responses.order_by(order_by)

    # Pagination
    paginator = Paginator(responses, per_page)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    forms_list = FeedbackForm.objects.filter(
        hub_id=hub, is_deleted=False,
    ).order_by('name')

    context = {
        'responses': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_field': sort_field,
        'sort_dir': sort_dir,
        'form_filter': form_filter,
        'status_filter': status_filter,
        'forms_list': forms_list,
        'per_page': per_page,
    }

    # HTMX partial: swap only datatable body
    if request.headers.get('HX-Request') and request.headers.get('HX-Target') == 'datatable-body':
        return django_render(request, 'feedback/partials/responses_list.html', context)

    return context


# ============================================================================
# Response Detail
# ============================================================================

@login_required
def response_detail(request, response_id):
    """Response detail — renders in side panel via HTMX."""
    hub = _hub_id(request)
    response_obj = get_object_or_404(
        FeedbackResponse,
        id=response_id,
        hub_id=hub,
        is_deleted=False,
    )
    return django_render(request, 'feedback/partials/response_detail.html', {
        'response': response_obj,
    })


# ============================================================================
# Response Review
# ============================================================================

@login_required
@require_POST
def response_review(request, response_id):
    """Mark a response as reviewed or actioned."""
    hub = _hub_id(request)
    user_id = _user_id(request)
    response_obj = get_object_or_404(
        FeedbackResponse,
        id=response_id,
        hub_id=hub,
        is_deleted=False,
    )

    action = request.POST.get('action', 'reviewed')
    staff_notes = request.POST.get('staff_notes', '').strip()

    if staff_notes:
        response_obj.staff_notes = staff_notes

    if action == 'actioned':
        response_obj.mark_actioned(reviewer_id=user_id)
        messages.success(request, _('Response marked as actioned'))
    else:
        response_obj.mark_reviewed(reviewer_id=user_id)
        messages.success(request, _('Response marked as reviewed'))

    if staff_notes:
        response_obj.save(update_fields=['staff_notes', 'updated_at'])

    return _render_responses_list(request, hub)


# ============================================================================
# Response Delete
# ============================================================================

@login_required
@require_POST
def response_delete(request, response_id):
    """Soft delete a feedback response."""
    hub = _hub_id(request)
    response_obj = get_object_or_404(
        FeedbackResponse,
        id=response_id,
        hub_id=hub,
        is_deleted=False,
    )
    response_obj.is_deleted = True
    response_obj.deleted_at = timezone.now()
    response_obj.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    messages.success(request, _('Response deleted successfully'))
    return _render_responses_list(request, hub)


# ============================================================================
# Response Bulk Action
# ============================================================================

@login_required
@require_POST
def response_bulk_action(request):
    """Bulk mark reviewed, actioned, or delete responses."""
    hub = _hub_id(request)
    user_id = _user_id(request)
    ids_str = request.POST.get('ids', '')
    action = request.POST.get('action', '')

    if not ids_str or not action:
        return _render_responses_list(request, hub)

    ids = [uid.strip() for uid in ids_str.split(',') if uid.strip()]
    responses = FeedbackResponse.objects.filter(
        hub_id=hub, id__in=ids, is_deleted=False,
    )
    count = responses.count()

    if action == 'reviewed':
        responses.update(
            status='reviewed',
            reviewed_by=user_id,
            reviewed_at=timezone.now(),
        )
        messages.success(request, _('%(count)d responses marked as reviewed') % {'count': count})
    elif action == 'actioned':
        responses.update(
            status='actioned',
            reviewed_by=user_id,
            reviewed_at=timezone.now(),
        )
        messages.success(request, _('%(count)d responses marked as actioned') % {'count': count})
    elif action == 'delete':
        responses.update(is_deleted=True, deleted_at=timezone.now())
        messages.success(request, _('%(count)d responses deleted') % {'count': count})

    return _render_responses_list(request, hub)


# ============================================================================
# Forms List
# ============================================================================

@login_required
@with_module_nav('feedback', 'forms')
@htmx_view('feedback/pages/forms_list.html', 'feedback/partials/forms_content.html')
def forms_list(request):
    """List of feedback forms."""
    hub = _hub_id(request)

    feedback_forms = FeedbackForm.objects.filter(
        hub_id=hub, is_deleted=False,
    ).annotate(
        total_responses=Count(
            'responses',
            filter=Q(responses__is_deleted=False),
        ),
    ).order_by('-created_at')

    return {
        'feedback_forms': feedback_forms,
    }


# ============================================================================
# Form CRUD
# ============================================================================

@login_required
def form_add(request):
    """Add feedback form — renders in side panel via HTMX."""
    hub = _hub_id(request)

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'feedback/partials/panel_form_add.html')

        FeedbackForm.objects.create(
            hub_id=hub,
            name=name,
            description=request.POST.get('description', '').strip(),
            form_type=request.POST.get('form_type', 'stars_5'),
            trigger_type=request.POST.get('trigger_type', 'manual'),
            trigger_delay_hours=int(request.POST.get('trigger_delay_hours', '24') or '24'),
            include_comment=request.POST.get('include_comment') == 'on',
            is_active=request.POST.get('is_active') != 'off',
            thank_you_message=request.POST.get('thank_you_message', '').strip(),
        )
        messages.success(request, _('Feedback form created successfully'))
        return _render_forms_list_items(request, hub)

    return django_render(request, 'feedback/partials/panel_form_add.html')


@login_required
def form_edit(request, form_id):
    """Edit feedback form — renders in side panel via HTMX."""
    hub = _hub_id(request)
    feedback_form = get_object_or_404(
        FeedbackForm, id=form_id, hub_id=hub, is_deleted=False,
    )

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, _('Name is required'))
            return django_render(request, 'feedback/partials/panel_form_edit.html', {
                'feedback_form': feedback_form,
            })

        feedback_form.name = name
        feedback_form.description = request.POST.get('description', '').strip()
        feedback_form.form_type = request.POST.get('form_type', 'stars_5')
        feedback_form.trigger_type = request.POST.get('trigger_type', 'manual')
        feedback_form.trigger_delay_hours = int(request.POST.get('trigger_delay_hours', '24') or '24')
        feedback_form.include_comment = request.POST.get('include_comment') == 'on'
        feedback_form.is_active = request.POST.get('is_active') != 'off'
        feedback_form.thank_you_message = request.POST.get('thank_you_message', '').strip()
        feedback_form.save()

        messages.success(request, _('Feedback form updated successfully'))
        return _render_forms_list_items(request, hub)

    return django_render(request, 'feedback/partials/panel_form_edit.html', {
        'feedback_form': feedback_form,
    })


@login_required
@require_POST
def form_delete(request, form_id):
    """Soft delete a feedback form."""
    hub = _hub_id(request)
    feedback_form = get_object_or_404(
        FeedbackForm, id=form_id, hub_id=hub, is_deleted=False,
    )
    feedback_form.is_deleted = True
    feedback_form.deleted_at = timezone.now()
    feedback_form.save(update_fields=['is_deleted', 'deleted_at', 'updated_at'])

    messages.success(request, _('Feedback form deleted successfully'))
    return _render_forms_list_items(request, hub)


@login_required
@require_POST
def form_toggle(request, form_id):
    """Toggle a feedback form active/inactive."""
    hub = _hub_id(request)
    feedback_form = get_object_or_404(
        FeedbackForm, id=form_id, hub_id=hub, is_deleted=False,
    )
    feedback_form.is_active = not feedback_form.is_active
    feedback_form.save(update_fields=['is_active', 'updated_at'])

    status = _('activated') if feedback_form.is_active else _('deactivated')
    messages.success(request, _('Form %(status)s successfully') % {'status': status})
    return _render_forms_list_items(request, hub)


# ============================================================================
# Settings
# ============================================================================

@login_required
@with_module_nav('feedback', 'settings')
@htmx_view('feedback/pages/settings.html', 'feedback/partials/settings_content.html')
def settings_view(request):
    """Feedback module settings."""
    hub = _hub_id(request)
    settings_obj = FeedbackSettings.get_for_hub(hub)

    active_forms = FeedbackForm.objects.filter(
        hub_id=hub, is_deleted=False, is_active=True,
    ).order_by('name')

    total_responses = FeedbackResponse.objects.filter(
        hub_id=hub, is_deleted=False,
    ).count()
    total_forms = FeedbackForm.objects.filter(
        hub_id=hub, is_deleted=False,
    ).count()
    new_responses = FeedbackResponse.objects.filter(
        hub_id=hub, is_deleted=False, status='new',
    ).count()

    if request.method == 'POST':
        settings_obj.auto_send_post_sale = request.POST.get('auto_send_post_sale') == 'on'
        settings_obj.auto_send_post_appointment = request.POST.get('auto_send_post_appointment') == 'on'
        default_form_id = request.POST.get('default_form', '')
        if default_form_id:
            try:
                settings_obj.default_form = FeedbackForm.objects.get(
                    id=default_form_id, hub_id=hub, is_deleted=False,
                )
            except FeedbackForm.DoesNotExist:
                settings_obj.default_form = None
        else:
            settings_obj.default_form = None
        settings_obj.minimum_days_between_requests = int(
            request.POST.get('minimum_days_between_requests', '30') or '30'
        )
        settings_obj.save()
        messages.success(request, _('Settings saved successfully'))

    return {
        'settings_obj': settings_obj,
        'active_forms': active_forms,
        'total_responses': total_responses,
        'total_forms': total_forms,
        'new_responses': new_responses,
    }
