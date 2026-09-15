import uuid
import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from pricerequest.apps import PricerequestConfig


UserModel = get_user_model()


# ============================================================
# Metadata Abstract Classes
# Same pattern as PreDisclosure
# ============================================================

class MetaAbstract(models.Model):
    """
    Metadata base class.

    Provides:
        - Created By
        - Created Date
        - Last Edited By
        - Last Edited Date
    """

    meta_created_date = models.DateTimeField(
        auto_now=True,
        blank=True,
        verbose_name="Created At",
    )

    meta_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )

    meta_edited_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Edit At",
    )

    meta_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Last Edit By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_edited_by",
    )

    class Meta:
        abstract = True


class MetaCreatedAbstract(models.Model):
    """
    Metadata base class for records where only
    creation information is required.
    """

    meta_created_date = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name="Created At",
    )

    meta_created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created_by",
    )

    class Meta:
        abstract = True


class MetaEditedAbstract(models.Model):
    """
    Metadata base class for records where only
    edit information is required.
    """

    meta_edited_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Last Edit At",
    )

    meta_edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_edited_by",
    )

    class Meta:
        abstract = True


# ============================================================
# Ticket Number
# ============================================================

def ticket_number_generator():
    today = datetime.date.today().isoformat().replace("-", "")
    random_sequence = str(uuid.uuid4())[:5]
    return f"T{today}{random_sequence.upper()}"


# ============================================================
# Announcement Choices
# ============================================================

class AnnouncementTypeChoices(models.TextChoices):
    ITCG = ("ITCG", "ITCG")
    NSO = ("DRBG", "DRBG")
    ITCG_NSO = ("ITCG_DRBG", "ITCG_DRBG")
    NO_ANNOUNCEMENT = (
        "NO_ANNOUNCEMENT",
        "NO_ANNOUNCEMENT",
    )


# ============================================================
# Ticket Status Choices
# ============================================================

class TicketStatusChoices(models.TextChoices):
    DRAFT = "DRAFT", "DRAFT"

    CONFIRMED = "CONFIRMED", "CONFIRMED"

    PENDING_SALESOPS_VALIDATION = (
        "PENDING_SALESOPS_VALIDATION",
        "PENDING_SALESOPS_VALIDATION",
    )

    PENDING_SETUP = (
        "PENDING_SETUP",
        "PENDING_SETUP",
    )

    PENDING_ITCG_ANNOUNCEMENTS = (
        "PENDING_ITCG_ANNOUNCEMENTS",
        "PENDING_ITCG_ANNOUNCEMENTS",
    )

    DRBG_ANNOUNCEMENTS_COMPLETED = (
        "DRBG_ANNOUNCEMENTS_COMPLETED",
        "DRBG_ANNOUNCEMENTS_COMPLETED",
    )

    ITCG_ANNOUNCEMENTS_COMPLETED = (
        "ITCG_ANNOUNCEMENTS_COMPLETED",
        "ITCG_ANNOUNCEMENTS_COMPLETED",
    )

    PENDING_PM_VALIDATION = (
        "PENDING_PM_VALIDATION",
        "PENDING_PM_VALIDATION",
    )

    CLOSED = "CLOSED", "CLOSED"

    PM_REJECTED = (
        "PM_REJECTED",
        "PM_REJECTED",
    )

    SALESOPS_REJECTED = (
        "SALESOPS_REJECTED",
        "SALESOPS_REJECTED",
    )


# ============================================================
# SharePoint Upload Path
# ============================================================

def generate_upload_path(ticket_id: str) -> str:
    """
    SharePoint path generator to store
    Price Request attachments.
    """

    start_date = datetime.datetime.today().strftime(
        "%d-%m-%Y-%H-%M"
    )

    base_url = (
        f"{PricerequestConfig.site_address}"
        f"{PricerequestConfig.library}"
    )

    return f"{base_url}/{ticket_id}/"


# ============================================================
# Ticket
# ============================================================

class Ticket(MetaAbstract):

    ticket_number = models.CharField(
        max_length=30,
        primary_key=True,
        default=ticket_number_generator,
    )

    subject = models.CharField(
        max_length=140,
        null=True,
        verbose_name="Subject",
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep this temporarily for production compatibility.
    # Existing forms / APIs / code may still use this field.
    #
    # Data will be migrated to:
    #     meta_created_by
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Created By",
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep this temporarily for production compatibility.
    # Data will be migrated to:
    #     meta_edited_date
    # --------------------------------------------------------

    modified = models.DateTimeField(
        auto_now=True,
    )

    email_cc = models.TextField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name="Email CC",
    )

    elp_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="ELP Start Date",
    )

    cif_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="CIF Start Date",
    )

    influencer_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="INFL Start Date",
    )

    tp_launch_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="TP Launch Date",
    )

    ecom_launch_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Ecom Launch Date",
    )

    # --------------------------------------------------------
    # comments -> comment
    #
    # IMPORTANT:
    # db_column keeps the existing database column as
    # "comments", so existing production data is preserved.
    # --------------------------------------------------------

    comment = models.TextField(
        max_length=400,
        blank=True,
        null=True,
        db_column="comments",
        verbose_name="Comment",
    )

    is_annoucement = models.BooleanField(
        blank=False,
        null=False,
        default=True,
        verbose_name="Announcement(Y/N)",
    )

    announcement_choice = models.CharField(
        max_length=20,
        blank=True,
        null=False,
        default=AnnouncementTypeChoices.NO_ANNOUNCEMENT,
        choices=AnnouncementTypeChoices,
        verbose_name="Announcement Choice",
    )

    link = models.URLField(
        max_length=3000,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.ticket_number

    def save(self, *args, **kwargs):
        self.link = generate_upload_path(
            ticket_id=self.ticket_number
        )
        super().save(*args, **kwargs)


# ============================================================
# Ticket Line
#
# IMPORTANT:
# There is NO TicketLine status.
# Ticket status is maintained separately in TicketStatus.
# ============================================================

class TicketLine(MetaAbstract):

    ticket_number = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="ticket_lines",
        verbose_name="Ticket Number",
    )

    product_group = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        verbose_name="Product Group",
    )

    product_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="Product Name",
    )

    mercury = models.CharField(
        max_length=10,
        blank=False,
        null=True,
        verbose_name="Mercury",
    )

    model_budget = models.CharField(
        max_length=200,
        blank=False,
        null=True,
        verbose_name="Model Budget",
    )

    pelp_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="ELP",
    )

    cee_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="CEE",
    )

    cea_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="CEA",
    )

    cme_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="CME",
    )

    csa_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="CSA",
    )

    influencer_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="INFL",
    )

    tp_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="TP",
    )

    rsp_baseline = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="RSP Baseline",
    )

    rsp_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="RSP",
    )

    def __str__(self):
        return f"{self.ticket_number} - {self.mercury}"

    class Meta:
        verbose_name = "Ticket Line"
        verbose_name_plural = "Ticket Lines"


# ============================================================
# Ticket Status
# ============================================================

class TicketStatus(MetaCreatedAbstract):

    ticket_number = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name="ticket_status",
    )

    status = models.CharField(
        max_length=30,
        choices=TicketStatusChoices,
        null=False,
        blank=False,
        default=TicketStatusChoices.DRAFT,
        verbose_name="Ticket Status",
    )

    # --------------------------------------------------------
    # comments -> comment
    #
    # Keep existing DB column "comments".
    # --------------------------------------------------------

    comment = models.CharField(
        max_length=1000,
        null=True,
        blank=True,
        db_column="comments",
        verbose_name="Comment",
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep temporarily for production compatibility.
    # Data will be migrated to:
    #     meta_created_by
    # --------------------------------------------------------

    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep temporarily for production compatibility.
    # Data will be migrated to:
    #     meta_created_date
    # --------------------------------------------------------

    modified = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.ticket_number} - {self.status}"

    class Meta:
        verbose_name = "Ticket Status"
        verbose_name_plural = "Ticket Statuses"


# ============================================================
# CCI Price List
#
# External / unmanaged table.
# DO NOT add metadata fields here.
# ============================================================

class CCIPriceList(models.Model):

    price_list_name = models.CharField(
        db_column="PRICE_LIST_NAME",
        primary_key=True,
        max_length=80,
        blank=False,
        null=False,
    )

    list_header_id = models.IntegerField(
        db_column="LIST_HEADER_ID",
        blank=True,
        null=True,
    )

    list_line_id = models.CharField(
        db_column="LIST_LINE_ID",
        max_length=60,
        blank=True,
        null=True,
    )

    currency_code = models.CharField(
        db_column="CURRENCY_CODE",
        max_length=40,
        blank=True,
        null=True,
    )

    ln_start_date_active = models.DateTimeField(
        db_column="LN_START_DATE_ACTIVE",
        blank=True,
        null=True,
    )

    ln_end_date_active = models.DateTimeField(
        db_column="LN_END_DATE_ACTIVE",
        blank=True,
        null=True,
    )

    list_price = models.DecimalField(
        db_column="LIST_PRICE",
        max_digits=8,
        decimal_places=7,
        null=True,
        blank=True,
    )

    product_attr_value = models.CharField(
        db_column="PRODUCT_ATTR_VALUE",
        max_length=70,
        blank=True,
        null=True,
    )

    mercury_code = models.CharField(
        db_column="MERCURY_CODE",
        max_length=30,
        blank=True,
        null=True,
    )

    pricingline_creation_date = models.DateTimeField(
        db_column="PricingLine_CREATION_DATE",
        blank=True,
        null=True,
    )

    pricingline_created_by = models.CharField(
        db_column="PricingLine_CREATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricingline_created_by_user = models.CharField(
        db_column="PricingLine_CREATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    pricingline_last_update_date = models.DateTimeField(
        db_column="PricingLine_LAST_UPDATE_DATE",
        blank=True,
        null=True,
    )

    pricingline_last_updated_by = models.CharField(
        db_column="PricingLine_LAST_UPDATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricingline_last_updated_by_user = models.CharField(
        db_column="PricingLine_LAST_UPDATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelist_creation_date = models.DateTimeField(
        db_column="PriceList_CREATION_DATE",
        blank=True,
        null=True,
    )

    pricelist_created_by = models.CharField(
        db_column="PriceList_CREATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelist_created_by_user = models.CharField(
        db_column="PriceList_CREATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelist_last_update_date = models.DateTimeField(
        db_column="PriceList_LAST_UPDATE_DATE",
        blank=True,
        null=True,
    )

    pricelist_last_updated_by = models.CharField(
        db_column="PriceList_LAST_UPDATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelist_last_updated_by_user = models.CharField(
        db_column="PriceList_LAST_UPDATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelistname_creation_date = models.DateTimeField(
        db_column="PriceListName_CREATION_DATE",
        blank=True,
        null=True,
    )

    pricelistname_created_by = models.CharField(
        db_column="PriceListName_CREATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelistname_created_by_user = models.CharField(
        db_column="PriceListName_CREATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelistname_last_update_date = models.DateTimeField(
        db_column="PriceListName_LAST_UPDATE_DATE",
        blank=True,
        null=True,
    )

    pricelistname_last_updated_by = models.CharField(
        db_column="PriceListName_LAST_UPDATED_BY",
        max_length=60,
        blank=True,
        null=True,
    )

    pricelistname_last_updated_by_user = models.CharField(
        db_column="PriceListName_LAST_UPDATED_BY_USER",
        max_length=60,
        blank=True,
        null=True,
    )

    record_date = models.DateTimeField(
        db_column="Record_date",
        blank=True,
        null=True,
    )

    source_file = models.CharField(
        db_column="Source_File",
        max_length=60,
        blank=True,
        null=True,
    )

    mercury_code_8 = models.CharField(
        db_column="MERCURY_CODE_8",
        max_length=8,
        blank=True,
        null=True,
    )

    datasource = models.CharField(
        db_column="DataSource",
        max_length=60,
        blank=True,
        null=True,
    )

    def __str__(self):
        return (
            f"{self.price_list_name} - "
            f"{self.mercury_code_8} - "
            f"{self.pricelistname_creation_date}"
        )

    class Meta:
        managed = False
        db_table = "CCI_Price_List"


# ============================================================
# Contact Email Choices
# ============================================================

class UserTypeChoices(models.TextChoices):
    DRBG = ("DRBG", "ER")
    ITCG = ("ITCG", "DR")


# ============================================================
# Contact Emails
#
# Created metadata only.
# ============================================================

class ContactEmails(MetaCreatedAbstract):
    """
    Entries to display in DRBG/ITCG Group Email section.
    """

    user_type = models.CharField(
        max_length=50,
        choices=UserTypeChoices,
        null=False,
        blank=False,
    )

    group_name = models.CharField(
        max_length=400,
        null=False,
        blank=False,
    )

    group_email = models.CharField(
        max_length=140,
        null=False,
        blank=False,
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep temporarily for production compatibility.
    # Data will be migrated to:
    #     meta_created_by
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user_type} - {self.group_name}"

    class Meta:
        verbose_name = "DR/ER Group Contact"
        verbose_name_plural = "DR/ER Group Contacts"


# ============================================================
# Announcement Mail Link
#
# Created metadata only.
# ============================================================

class AnnouncementMailLink(MetaCreatedAbstract):

    user_type = models.CharField(
        max_length=50,
        choices=UserTypeChoices,
        null=False,
        blank=False,
    )

    link_name = models.CharField(
        max_length=400,
        null=False,
        blank=False,
    )

    link_url = models.CharField(
        max_length=1000,
        null=False,
        blank=False,
    )

    # --------------------------------------------------------
    # LEGACY FIELD
    #
    # Keep temporarily for production compatibility.
    # Data will be migrated to:
    #     meta_created_by
    # --------------------------------------------------------

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name="Created By",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user_type} - {self.link_name}"

    class Meta:
        verbose_name = "DR/ER Announcement Mail Link"
        verbose_name_plural = "DR/ER Announcement Mail Links"
