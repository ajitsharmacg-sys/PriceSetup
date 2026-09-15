from collections import defaultdict

from pricerequest.roles import (
    PM_USER,
    SALES_OPS_USER,
    ADMIN_ROLE,
)

from pricerequest.models import (
    TicketStatusChoices,
)


# ---------------------------------------------------------
# Status Graph
# ---------------------------------------------------------

TICKET_STATUS_GRAPH = {
    TicketStatusChoices.DRAFT: [
        TicketStatusChoices.PENDING_SALESOPS_VALIDATION,
    ],

    TicketStatusChoices.PENDING_SALESOPS_VALIDATION: [
        TicketStatusChoices.PENDING_SETUP,
        TicketStatusChoices.PENDING_DRBG_ANNOUNCEMENTS,
        TicketStatusChoices.PENDING_ITCG_ANNOUNCEMENTS,
        TicketStatusChoices.REJECTED,
    ],

    TicketStatusChoices.PENDING_SETUP: [
        TicketStatusChoices.PENDING_PM_VALIDATION,
        TicketStatusChoices.REJECTED,
    ],

    TicketStatusChoices.PENDING_DRBG_ANNOUNCEMENTS: [
        TicketStatusChoices.PENDING_ITCG_ANNOUNCEMENTS,
        TicketStatusChoices.PENDING_PM_VALIDATION,
    ],

    TicketStatusChoices.PENDING_ITCG_ANNOUNCEMENTS: [
        TicketStatusChoices.PENDING_PM_VALIDATION,
    ],

    TicketStatusChoices.PENDING_PM_VALIDATION: [
        TicketStatusChoices.CLOSED,
        TicketStatusChoices.REJECTED,
    ],

    TicketStatusChoices.REJECTED: [
        TicketStatusChoices.DRAFT,
    ],

    TicketStatusChoices.CLOSED: [],
}


# ---------------------------------------------------------
# Status -> Roles
# ---------------------------------------------------------

TICKET_STATUS_TO_ROLE = {
    TicketStatusChoices.DRAFT: [
        PM_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.PENDING_SALESOPS_VALIDATION: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.PENDING_SETUP: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.PENDING_DRBG_ANNOUNCEMENTS: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.PENDING_ITCG_ANNOUNCEMENTS: [
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.PENDING_PM_VALIDATION: [
        PM_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.CLOSED: [
        PM_USER,
        ADMIN_ROLE,
    ],

    TicketStatusChoices.REJECTED: [
        PM_USER,
        SALES_OPS_USER,
        ADMIN_ROLE,
    ],
}


# ---------------------------------------------------------
# Role -> Status
# ---------------------------------------------------------

def build_role_to_status_mapping(status_to_role):
    role_to_status = defaultdict(list)

    for status, roles in status_to_role.items():
        for role in roles:
            role_to_status[role].append(status)

    return dict(role_to_status)


ROLE_TO_TICKET_STATUS = build_role_to_status_mapping(
    TICKET_STATUS_TO_ROLE
)


# ---------------------------------------------------------
# Generic Workflow Helpers
# ---------------------------------------------------------

def get_available_transitions(
    current_status,
    status_graph,
):
    return status_graph.get(
        current_status,
        [],
    )


def is_valid_transition(
    current_status,
    new_status,
    status_graph,
):
    return new_status in get_available_transitions(
        current_status=current_status,
        status_graph=status_graph,
    )


def is_role_allowed_for_status(
    user_roles,
    target_status,
    status_to_role,
):
    allowed_roles = status_to_role.get(
        target_status,
        [],
    )

    return bool(
        set(user_roles).intersection(
            allowed_roles
        )
    )


# ---------------------------------------------------------
# Ticket Workflow Helpers
# ---------------------------------------------------------

def is_valid_ticket_transition(
    current_status,
    new_status,
):
    return is_valid_transition(
        current_status=current_status,
        new_status=new_status,
        status_graph=TICKET_STATUS_GRAPH,
    )


def is_role_allowed_for_ticket_status(
    user_roles,
    target_status,
):
    return is_role_allowed_for_status(
        user_roles=user_roles,
        target_status=target_status,
        status_to_role=TICKET_STATUS_TO_ROLE,
    )
