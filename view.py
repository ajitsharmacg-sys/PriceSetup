from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from common.apps import CommonConfig
from common.views import forbidden_page
from common.models import ContactOrLink

from pricerequest.forms import (
    TicketForm,
    TicketLineForm,
)
from pricerequest.apps import PricerequestConfig
from pricerequest.roles import (
    ROLES,
    PM_USER,
    ADMIN_ROLE,
)
from pricerequest.workflow import (
    TICKET_STATUS_GRAPH,
    TICKET_STATUS_TO_ROLE,
    ROLE_TO_TICKET_STATUS,
)

from django.contrib.auth import get_user_model


UserModel = get_user_model()


def has_access_to_price_request_tool(user):
    if user.groups.filter(name__in=ROLES).exists():
        return True

    return False


def get_default_context(request):
    app_prefix = "Price Request"

    users = UserModel.objects.filter(
        groups__name__in=[
            PM_USER,
            ROLES,
            ADMIN_ROLE,
        ]
    ).distinct()

    users_to_display = []

    for user in users:
        u = {}

        u["email"] = user.email
        u["first_name"] = user.first_name
        u["last_name"] = user.last_name
        u["roles"] = []

        for group in user.groups.all():
            if app_prefix in group.name:
                u["roles"].append(group.name)

        u["roles"] = ", ".join(u["roles"])
        users_to_display.append(u)

    context = {
        "price_request_form": TicketForm(),
        "ticket_line_form": TicketLineForm(),

        "site_address": PricerequestConfig.site_address,
        "library": PricerequestConfig.library,

        "sharepoint_upload_endpoint": settings.AZURE_SECRETS[
            "SharepointUploadEndpoint"
        ],

        "users_to_display": users_to_display,

        "links": ContactOrLink.objects.filter(
            related_to_app=PricerequestConfig.name
        ),

        "feedback_site_address": CommonConfig.feedback_site_address,
        "feedback_library": CommonConfig.feedback_library,

        "app_name": PricerequestConfig.name,
    }

    return context


@login_required
def price_request_index(request, context=None):

    if not has_access_to_price_request_tool(
        UserModel.objects.get(id=request.user.id)
    ):
        return forbidden_page(request, ROLES)

    default_context = get_default_context(request)

    if not context:
        context = default_context
    else:
        context = context | default_context

    return render(
        request,
        "pricerequest/app.html",
        context=context,
    )


@login_required
def ticket_number(request, ticket_number):
    return price_request_index(
        request,
        context={
            "ticket_number": ticket_number,
            "start_screen": "ticket_info",
        },
    )


@login_required
def workflow(request):
    workflow = {
        "TICKET_STATUS_GRAPH": TICKET_STATUS_GRAPH,
        "TICKET_STATUS_TO_ROLE": TICKET_STATUS_TO_ROLE,
        "ROLE_TO_TICKET_STATUS": ROLE_TO_TICKET_STATUS,
        "ROLES": ROLES,
        "ADMIN_ROLE": ADMIN_ROLE,
    }

    return JsonResponse(workflow)
