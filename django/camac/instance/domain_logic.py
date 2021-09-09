import json
from uuid import uuid4

from caluma.caluma_form import api as form_api, models as form_models
from caluma.caluma_workflow import api as workflow_api, models as workflow_models
from django.conf import settings
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.core.files.base import ContentFile
from django.db.models import Max, Q
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from camac.caluma.api import CalumaApi
from camac.caluma.extensions.data_sources import Municipalities
from camac.constants import kt_bern as be_constants, kt_uri as ur_constants
from camac.core.models import (
    Answer,
    InstanceLocation,
    InstanceService,
    WorkflowEntry,
    WorkflowItem,
)
from camac.instance.models import Instance
from camac.user.permissions import permission_aware

from . import models

SUBMIT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
WORKFLOW_ITEM_DOSSIER_ERFASST_UR = 12

caluma_api = CalumaApi()


class CreateInstanceLogic:
    @classmethod
    @permission_aware
    def validate(cls, data, group):
        return data

    @classmethod
    def validate_for_municipality(cls, data, group):
        if settings.APPLICATION["CALUMA"].get("CREATE_IN_PROCESS"):
            data["instance_state"] = models.InstanceState.objects.get(name="comm")

        if settings.APPLICATION["CALUMA"].get("USE_LOCATION"):
            if (
                data.get("location", False)
                and data["location"] not in group.locations.all()
            ):
                raise ValidationError(
                    "Provided location is not present in group locations"
                )

            data["location"] = data.get("location", group.locations.first())

        return data

    @classmethod
    def validate_for_coordination(cls, data, group):  # pragma: no cover
        if settings.APPLICATION["CALUMA"].get("CREATE_IN_PROCESS"):
            # FIXME: Bundesstelle has role "coordination, but is
            # actually more like a municipality (dossiers start in COMM)
            is_federal = group.service.pk == ur_constants.BUNDESSTELLE_SERVICE_ID
            state = "comm" if is_federal else "ext"
            data["instance_state"] = models.InstanceState.objects.get(name=state)

        return data

    @staticmethod
    def update_instance_location(instance):
        """
        Set the location also in the InstanceLocation table.

        The API uses the location directly on the instance,
        but some Camac core functions need the location in
        the InstanceLocation table.
        """
        InstanceLocation.objects.filter(instance=instance).delete()
        if instance.location_id is not None:
            InstanceLocation.objects.create(
                instance=instance, location_id=instance.location_id
            )

    def generate_identifier(instance, year=None):
        """
        Build identifier for instance.

        Format for normal forms:
        two last digits of communal location number
        year in two digits
        unique sequence
        Example: 11-18-001

        Format for special forms:
        two letter abbreviation of form
        year in two digits
        unique sequence
        Example: AV-20-014
        """
        identifier = instance.identifier
        if not identifier:
            year = (year or timezone.now().year) % 100

            name = instance.form.name
            abbreviations = settings.APPLICATION.get(
                "INSTANCE_IDENTIFIER_FORM_ABBR", {}
            )
            meta = models.FormField.objects.filter(
                instance=instance, name="meta"
            ).first()
            if meta:
                meta_value = json.loads(meta.value)
                name = meta_value["formType"]

            if name in abbreviations.keys():
                identifier_start = abbreviations[name]
            elif settings.APPLICATION.get("SHORT_DOSSIER_NUMBER", False):
                identifier_start = instance.location.communal_federal_number[-2:]
            else:
                identifier_start = instance.location.communal_federal_number

            start = "{0}-{1}-".format(identifier_start, year)

            if settings.APPLICATION["CALUMA"].get("SAVE_DOSSIER_NUMBER_IN_CALUMA"):
                max_identifier = (
                    workflow_models.Case.objects.filter(
                        **{"meta__dossier-number__startswith": start}
                    )
                    .annotate(dossier_nr=KeyTextTransform("dossier-number", "meta"))
                    .aggregate(max_identifier=Max("dossier_nr"))["max_identifier"]
                    or "00-00-000"
                )
            else:
                max_identifier = (
                    models.Instance.objects.filter(
                        identifier__startswith=start
                    ).aggregate(max_identifier=Max("identifier"))["max_identifier"]
                    or "00-00-000"
                )

            sequence = int(max_identifier[-3:])

            identifier = "{0}-{1}-{2}".format(
                identifier_start, str(year).zfill(2), str(sequence + 1).zfill(3)
            )

        return identifier

    @classmethod
    @permission_aware
    def should_generate_identifier(cls, group):
        return False

    @classmethod
    def should_generate_identifier_for_municipality(cls, group):
        return settings.APPLICATION["CALUMA"].get("GENERATE_IDENTIFIER")

    @classmethod
    def should_generate_identifier_for_coordination(cls, group):
        return settings.APPLICATION["CALUMA"].get("GENERATE_IDENTIFIER")

    @staticmethod
    def set_creation_date(instance, validated_data):
        perms = settings.APPLICATION.get("ROLE_PERMISSIONS", {})
        if perms.get(validated_data["group"].role.name) in [
            "coordination",
            "municipality",
        ]:
            creation_date = timezone.now().strftime(SUBMIT_DATE_FORMAT)
            workflow_item = WorkflowItem.objects.get(
                pk=WORKFLOW_ITEM_DOSSIER_ERFASST_UR
            )

            WorkflowEntry.objects.create(
                workflow_date=creation_date,
                instance=instance,
                workflow_item=workflow_item,
                group=1,
            )
            CalumaApi().set_submit_date(instance.pk, creation_date)

    @staticmethod
    def initialize_caluma(
        instance,
        source_instance,
        case,
        is_modification,
        is_paper,
        group,
        user,
        lead,
    ):

        if source_instance:
            old_document = case.document
            new_document = caluma_api.copy_document(
                source_instance.case.document.pk,
                exclude_form_slugs=(
                    ["6-dokumente", "7-bestaetigung", "8-freigabequittung"]
                    if is_modification
                    else ["8-freigabequittung"]
                ),
            )
            new_document.form = old_document.form
            new_document.save()

            case.document = new_document
            case.save()
            old_document.delete()

        caluma_api.update_or_create_answer(
            case.document,
            "is-paper",
            "is-paper-yes" if is_paper else "is-paper-no",
            user,
        )

        if settings.APPLICATION["CALUMA"].get("SYNC_FORM_TYPE"):
            form_type = ur_constants.CALUMA_FORM_MAPPING.get(instance.form.pk)
            if not form_type:
                raise RuntimeError(
                    f"Unmapped form {instance.form.name} (ID {instance.form.pk})"
                )  # pragma: no cover

            caluma_api.update_or_create_answer(
                case.document,
                "form-type",
                "form-type-" + form_type,
                user,
            )

        if settings.APPLICATION["CALUMA"].get("HAS_PROJECT_CHANGE"):
            caluma_api.update_or_create_answer(
                case.document,
                "projektaenderung",
                "projektaenderung-ja" if is_modification else "projektaenderung-nein",
                user,
            )

        if settings.APPLICATION["CALUMA"].get("USE_LOCATION") and instance.location:
            caluma_api.update_or_create_answer(
                case.document,
                "municipality",
                str(instance.location.pk),
                user,
            )

            # Synchronize the 'Leitbehörde' for display in the dashboard
            caluma_api.update_or_create_answer(
                case.document,
                "leitbehoerde",
                str(lead),
                user,
            )

        if group.pk == settings.APPLICATION.get("PORTAL_GROUP", False):
            # TODO pre-fill user data into personal data table
            pass

        if is_paper:
            # prefill municipality question if possible
            value = str(group.service.pk)
            source = Municipalities()

            if source.validate_answer_value(value, case.document, "gemeinde", None):
                caluma_api.update_or_create_answer(
                    case.document,
                    "gemeinde",
                    value,
                    user,
                )

    @staticmethod
    def copy_applicants(source, target):
        for applicant in source.involved_applicants.all():
            target.involved_applicants.update_or_create(
                invitee=applicant.invitee,
                defaults={
                    "created": timezone.now(),
                    "user": applicant.user,
                    "email": applicant.email,
                },
            )

    @staticmethod
    def copy_attachments(source, target):
        for attachment in source.attachments.all():
            try:
                new_file = ContentFile(attachment.path.read())
            except FileNotFoundError:  # pragma: no cover
                # file does not exist so use the old file
                new_file = attachment.path

            # store sections first
            sections = attachment.attachment_sections.all()

            # copy the file
            new_file.name = attachment.path.name
            attachment.path = new_file

            attachment.attachment_id = None
            attachment.instance = target
            attachment.uuid = uuid4()
            attachment.save()

            attachment.attachment_sections.set(sections)
            attachment.save()

    @staticmethod
    def copy_ebau_number(source_instance, target_instance, case):
        ebau_number = caluma_api.get_ebau_number(source_instance)
        case.meta["ebau-number"] = ebau_number
        case.save()
        Answer.objects.create(
            instance=target_instance,
            question_id=be_constants.QUESTION_EBAU_NR_EXISTS,
            chapter_id=be_constants.CHAPTER_EBAU_NR,
            item=1,
            answer="yes",
        )
        Answer.objects.create(
            instance=target_instance,
            question_id=be_constants.QUESTION_EBAU_NR,
            chapter_id=be_constants.CHAPTER_EBAU_NR,
            item=1,
            answer=ebau_number,
        )

    @staticmethod
    def copy_extend_validity_answers(source, target, user):
        old_document = source.case.document
        new_document = target.case.document

        for answer in old_document.answers.filter(
            question_id__in=settings.APPLICATION["CALUMA"].get(
                "EXTEND_VALIDITY_COPY_QUESTIONS", []
            )
        ):
            form_api.save_answer(
                answer.question,
                new_document,
                user,
                answer.value,
            )

        for slug in settings.APPLICATION["CALUMA"].get(
            "EXTEND_VALIDITY_COPY_TABLE_QUESTIONS", []
        ):
            caluma_api.copy_table_answer(slug, slug, old_document, new_document)

        form_api.save_answer(
            form_models.Question.objects.get(pk="dossiernummer"),
            new_document,
            user,
            int(source.pk),
        )

    @staticmethod
    def initialize_camac(
        instance,
        source_instance,
        group,
        is_modification,
        is_paper,
        extend_validity_for,
        case,
        user,
    ):

        if is_paper:
            # remove the previously created applicants
            instance.involved_applicants.all().delete()

            # create instance service for permissions
            InstanceService.objects.create(
                instance=instance,
                service_id=group.service.pk,
                active=1,
                activation_date=None,
            )

        if source_instance and not is_modification:
            CreateInstanceLogic.copy_applicants(source_instance, instance)
            CreateInstanceLogic.copy_attachments(source_instance, instance)
        elif extend_validity_for:
            extend_validity_instance = models.Instance.objects.get(
                pk=extend_validity_for
            )
            CreateInstanceLogic.copy_ebau_number(
                extend_validity_instance, instance, case
            )
            CreateInstanceLogic.copy_extend_validity_answers(
                extend_validity_instance, instance, user
            )

    @staticmethod
    def create(
        data,
        caluma_user,
        camac_user,
        group,
        lead=None,
        is_modification=False,
        is_paper=False,
        caluma_form=None,
        source_instance=None,
        copy_source=False,
    ):
        """Create an instance.

        We assume that the caller can be trusted, so basic validations
        (e.g. if user is allowed to create a copy of the given source instance)
        are skipped here and performed in the serializer instead.
        """
        extend_validity_for = data.pop("extend_validity_for", None)

        form = data.get("form")
        if form and form.pk in settings.APPLICATION.get("ARCHIVE_FORMS", []):
            data["instance_state"] = models.InstanceState.objects.get(name="old")

        year = data.pop("year", None)

        instance = Instance.objects.create(**data)

        instance.involved_applicants.create(
            user=camac_user,
            invitee=camac_user,
            created=timezone.now(),
            email=camac_user.email,
        )

        if settings.APPLICATION["CALUMA"].get("USE_LOCATION"):  # pragma: no cover
            CreateInstanceLogic.update_instance_location(instance)

        workflow = workflow_models.Workflow.objects.filter(
            Q(allow_forms__in=[caluma_form]) | Q(allow_all_forms=True)
        ).first()

        case_meta = {"camac-instance-id": instance.pk}

        if CreateInstanceLogic.should_generate_identifier(group=group):
            # Give dossier a unique dossier number
            case_meta["dossier-number"] = CreateInstanceLogic.generate_identifier(
                instance, year
            )

        case = workflow_api.start_case(
            workflow=workflow,
            form=form_models.Form.objects.get(pk=caluma_form),
            user=caluma_user,
            meta=case_meta,
        )

        instance.case = case
        instance.save()

        # Reuse the SET_SUBMIT_DATE_CAMAC_WORKFLOW flag because since this defines the workflow date usage
        if settings.APPLICATION.get("SET_SUBMIT_DATE_CAMAC_WORKFLOW") and group:
            CreateInstanceLogic.set_creation_date(instance, data)

        CreateInstanceLogic.initialize_caluma(
            instance,
            source_instance,
            case,
            is_modification,
            is_paper,
            group,
            caluma_user,
            lead,
        )

        CreateInstanceLogic.initialize_camac(
            instance,
            source_instance,
            group,
            is_modification,
            is_paper,
            extend_validity_for,
            case,
            caluma_user,
        )

        return instance