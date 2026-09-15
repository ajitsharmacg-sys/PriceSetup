from django.core.management.base import BaseCommand
from django.db import transaction

from pricerequest.models import (
    Ticket,
    TicketStatus,
    ContactEmails,
    AnnouncementMailLink,
)


class Command(BaseCommand):
    help = (
        "Migrate legacy Price Request audit fields "
        "to metadata fields. Safe to run multiple times."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be updated without changing data.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        ticket_updates = 0
        status_updates = 0
        contact_updates = 0
        announcement_updates = 0

        with transaction.atomic():

            # ========================================================
            # Ticket
            # ========================================================

            for ticket in Ticket.objects.all().iterator():

                update_values = {}

                # created_by -> meta_created_by
                if (
                    ticket.meta_created_by_id is None
                    and ticket.created_by_id is not None
                ):
                    update_values["meta_created_by_id"] = (
                        ticket.created_by_id
                    )

                # modified -> meta_edited_date
                if (
                    ticket.meta_edited_date is None
                    and ticket.modified is not None
                ):
                    update_values["meta_edited_date"] = ticket.modified

                # ----------------------------------------------------
                # Ticket has no historical created date.
                #
                # Use the earliest TicketStatus.modified as the
                # creation date when available.
                # Otherwise use Ticket.modified.
                # ----------------------------------------------------
                if ticket.meta_created_date is None:

                    first_status = (
                        TicketStatus.objects
                        .filter(
                            ticket_number_id=ticket.ticket_number
                        )
                        .order_by("modified")
                        .values("modified")
                        .first()
                    )

                    created_date = None

                    if first_status:
                        created_date = first_status["modified"]

                    if created_date is None:
                        created_date = ticket.modified

                    if created_date is not None:
                        update_values["meta_created_date"] = (
                            created_date
                        )

                if update_values:
                    ticket_updates += 1

                    if not dry_run:
                        Ticket.objects.filter(
                            pk=ticket.ticket_number
                        ).update(**update_values)

            # ========================================================
            # TicketStatus
            # ========================================================

            for status in TicketStatus.objects.all().iterator():

                update_values = {}

                # modified_by -> meta_created_by
                if (
                    status.meta_created_by_id is None
                    and status.modified_by_id is not None
                ):
                    update_values["meta_created_by_id"] = (
                        status.modified_by_id
                    )

                # modified -> meta_created_date
                if (
                    status.meta_created_date is None
                    and status.modified is not None
                ):
                    update_values["meta_created_date"] = (
                        status.modified
                    )

                if update_values:
                    status_updates += 1

                    if not dry_run:
                        TicketStatus.objects.filter(
                            pk=status.pk
                        ).update(**update_values)

            # ========================================================
            # ContactEmails
            # ========================================================

            for contact in ContactEmails.objects.all().iterator():

                update_values = {}

                # created_by -> meta_created_by
                if (
                    contact.meta_created_by_id is None
                    and contact.created_by_id is not None
                ):
                    update_values["meta_created_by_id"] = (
                        contact.created_by_id
                    )

                if update_values:
                    contact_updates += 1

                    if not dry_run:
                        ContactEmails.objects.filter(
                            pk=contact.pk
                        ).update(**update_values)

            # ========================================================
            # AnnouncementMailLink
            # ========================================================

            for mail_link in AnnouncementMailLink.objects.all().iterator():

                update_values = {}

                # created_by -> meta_created_by
                if (
                    mail_link.meta_created_by_id is None
                    and mail_link.created_by_id is not None
                ):
                    update_values["meta_created_by_id"] = (
                        mail_link.created_by_id
                    )

                if update_values:
                    announcement_updates += 1

                    if not dry_run:
                        AnnouncementMailLink.objects.filter(
                            pk=mail_link.pk
                        ).update(**update_values)

            # --------------------------------------------------------
            # Roll back the transaction for dry-run.
            # --------------------------------------------------------
            if dry_run:
                transaction.set_rollback(True)

        # ============================================================
        # Output
        # ============================================================

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Price Request metadata migration"
            )
        )
        self.stdout.write("-" * 50)

        self.stdout.write(
            f"Tickets to update       : {ticket_updates}"
        )

        self.stdout.write(
            f"TicketStatus to update  : {status_updates}"
        )

        self.stdout.write(
            f"ContactEmails to update : {contact_updates}"
        )

        self.stdout.write(
            f"AnnouncementMailLink to update : "
            f"{announcement_updates}"
        )

        if dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING(
                    "DRY RUN - No database changes were made."
                )
            )
        else:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS(
                    "Migration completed successfully."
                )
            )
