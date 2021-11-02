from caluma.caluma_core.models import UUIDModel
from django.contrib.postgres.fields import JSONField
from django.db import models

from camac.dossier_import.messages import default_messages_object


def source_file_directory_path(dossier_import, filename):
    return "dossier_imports/files/{0}/{1}".format(str(dossier_import.id), filename)


class DossierImport(UUIDModel):
    """An import case for identification and recording results and meta info.

    We need to be able to identify import procedures including status,
    reports on success, failures and issues.
        - instance's `id`

    Imported dossiers (instance-case units) refer to this.
    Imports must be reproducible on another system (test -> prod)
    Associated import data (aka attachments) are located with this.

    """

    IMPORT_STATUS_NEW = "new"
    IMPORT_STATUS_DONE = "done"
    IMPORT_STATUS_VALIDATION_SUCCESSFUL = "verified"
    IMPORT_STATUS_VALIDATION_FAILED = "failed"
    IMPORT_STATUS_IMPORT_INPROGRESS = "in-progres"

    IMPORT_STATUS_CHOICES = (
        (IMPORT_STATUS_DONE, IMPORT_STATUS_DONE),
        (IMPORT_STATUS_NEW, IMPORT_STATUS_NEW),
        (IMPORT_STATUS_IMPORT_INPROGRESS, IMPORT_STATUS_IMPORT_INPROGRESS),
        (IMPORT_STATUS_VALIDATION_SUCCESSFUL, IMPORT_STATUS_VALIDATION_SUCCESSFUL),
        (IMPORT_STATUS_VALIDATION_FAILED, IMPORT_STATUS_VALIDATION_FAILED),
    )

    DOSSIER_LOADER_ZIP_ARCHIVE_XLSX = "zip-archive-xlsx"
    DOSSIER_LOADER_CHOICES = (
        (DOSSIER_LOADER_ZIP_ARCHIVE_XLSX, "XlsxFileDossierLoader"),
    )

    dossier_loader_type = models.CharField(
        max_length=255,
        choices=DOSSIER_LOADER_CHOICES,
        default=DOSSIER_LOADER_ZIP_ARCHIVE_XLSX,
    )

    status = models.CharField(
        max_length=32, choices=IMPORT_STATUS_CHOICES, default=IMPORT_STATUS_NEW
    )

    user = models.ForeignKey(
        "user.User",
        models.DO_NOTHING,
        related_name="dossier_imports",
        null=True,
        blank=True,
    )
    group = models.ForeignKey(
        "user.Group",
        models.DO_NOTHING,
        related_name="dossier_imports",
        null=True,
        blank=True,
    )
    service = models.ForeignKey(
        "user.Service", models.DO_NOTHING, related_name="+", null=True, blank=True
    )
    location = models.ForeignKey(
        "user.Location", models.DO_NOTHING, related_name="+", null=True, blank=True
    )

    messages = JSONField(default=default_messages_object)

    source_file = models.FileField(
        max_length=255, upload_to=source_file_directory_path, null=True, blank=True
    )

    mime_type = models.CharField(max_length=255, null=True, blank=True)
