"""AI tools for the Feedback module."""
from assistant.tools import AssistantTool, register_tool


@register_tool
class ListFeedbackForms(AssistantTool):
    name = "list_feedback_forms"
    description = "List feedback forms."
    module_id = "feedback"
    required_permission = "feedback.view_feedbackform"
    parameters = {
        "type": "object",
        "properties": {"is_active": {"type": "boolean"}, "form_type": {"type": "string"}},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from feedback.models import FeedbackForm
        qs = FeedbackForm.objects.all()
        if 'is_active' in args:
            qs = qs.filter(is_active=args['is_active'])
        if args.get('form_type'):
            qs = qs.filter(form_type=args['form_type'])
        return {"forms": [{"id": str(f.id), "name": f.name, "form_type": f.form_type, "trigger_type": f.trigger_type, "is_active": f.is_active} for f in qs]}


@register_tool
class CreateFeedbackForm(AssistantTool):
    name = "create_feedback_form"
    description = "Create a feedback form (e.g., NPS survey, post-sale rating)."
    module_id = "feedback"
    required_permission = "feedback.add_feedbackform"
    requires_confirmation = True
    parameters = {
        "type": "object",
        "properties": {
            "name": {"type": "string"}, "description": {"type": "string"},
            "form_type": {"type": "string", "description": "rating_5, nps_10, stars_5, thumbs, text_only"},
            "trigger_type": {"type": "string", "description": "manual, post_sale, post_appointment, post_ticket"},
            "include_comment": {"type": "boolean"}, "thank_you_message": {"type": "string"},
        },
        "required": ["name", "form_type"],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from feedback.models import FeedbackForm
        f = FeedbackForm.objects.create(
            name=args['name'], description=args.get('description', ''), form_type=args['form_type'],
            trigger_type=args.get('trigger_type', 'manual'),
            include_comment=args.get('include_comment', True),
            thank_you_message=args.get('thank_you_message', ''),
        )
        return {"id": str(f.id), "name": f.name, "created": True}


@register_tool
class ListFeedbackResponses(AssistantTool):
    name = "list_feedback_responses"
    description = "List feedback responses with filters."
    module_id = "feedback"
    required_permission = "feedback.view_feedbackresponse"
    parameters = {
        "type": "object",
        "properties": {
            "form_id": {"type": "string"}, "status": {"type": "string", "description": "new, reviewed, actioned"},
            "limit": {"type": "integer"},
        },
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from feedback.models import FeedbackResponse
        qs = FeedbackResponse.objects.select_related('form', 'customer').all()
        if args.get('form_id'):
            qs = qs.filter(form_id=args['form_id'])
        if args.get('status'):
            qs = qs.filter(status=args['status'])
        limit = args.get('limit', 20)
        return {
            "responses": [
                {"id": str(r.id), "form": r.form.name, "score": r.score, "comment": r.comment, "status": r.status, "created_at": r.created_at.isoformat()}
                for r in qs.order_by('-created_at')[:limit]
            ]
        }


@register_tool
class GetFeedbackSummary(AssistantTool):
    name = "get_feedback_summary"
    description = "Get feedback summary: average score, response count, breakdown."
    module_id = "feedback"
    required_permission = "feedback.view_feedbackresponse"
    parameters = {
        "type": "object",
        "properties": {"form_id": {"type": "string"}},
        "required": [],
        "additionalProperties": False,
    }

    def execute(self, args, request):
        from django.db.models import Avg, Count
        from feedback.models import FeedbackResponse
        qs = FeedbackResponse.objects.all()
        if args.get('form_id'):
            qs = qs.filter(form_id=args['form_id'])
        stats = qs.aggregate(avg_score=Avg('score'), total=Count('id'))
        by_status = dict(qs.values_list('status').annotate(c=Count('id')).values_list('status', 'c'))
        return {"avg_score": round(stats['avg_score'], 1) if stats['avg_score'] else None, "total_responses": stats['total'], "by_status": by_status}
