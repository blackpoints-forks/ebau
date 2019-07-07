from django.conf import settings
from django.db.models import Q
from django.db.models.constants import LOOKUP_SEP
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework import exceptions

from camac.attrs import nested_getattr
from camac.core.models import Circulation, InstanceService
from camac.mixins import AttributeMixin
from camac.request import get_request
from camac.user.permissions import permission_aware

from . import models


class InstanceQuerysetMixin(object):
    """
    Mixin to filter queryset by instances which may be read by given role.

    Define `instance_field` where instance is located on model (dot annotation)
    """

    instance_field = "instance"

    def _get_instance_filter_expr(self, field, expr=None):
        """Get filter expression of field on given model."""
        result = field

        if self.instance_field:
            instance_field = self.instance_field.replace(".", LOOKUP_SEP)
            result = instance_field + LOOKUP_SEP + result

        if expr:
            result = result + LOOKUP_SEP + expr

        return result

    def get_base_queryset(self):
        """Get base query queryset for role specific filters.

        Per default `self.queryset` is used but may be overwritten.
        """
        # instance state is always used to determine permissions
        instance_state_expr = self._get_instance_filter_expr("instance_state")
        return super().get_queryset().select_related(instance_state_expr)

    @permission_aware
    def get_queryset(self):
        queryset = self.get_base_queryset()
        user_field = self._get_instance_filter_expr(
            settings.APPLICATION["INSTANCE_USER_FIELD"]
        )
        return queryset.filter(**{user_field: self.request.user})

    def get_queryset_for_public_reader(self):
        queryset = self.get_base_queryset()
        instance_field = self._get_instance_filter_expr("pk", "in")

        # instances from municipality
        instances = models.Instance.objects.filter(
            location__in=self.request.group.locations.all(),
            publication_entries__publication_date__gt=timezone.now()
            - settings.APPLICATION.get("PUBLICATION_DURATION"),
            publication_entries__is_published=True,
        )

        return queryset.filter(**{instance_field: instances})

    def get_queryset_for_reader(self):
        return self.get_queryset_for_municipality()

    def get_queryset_for_municipality(self):
        queryset = self.get_base_queryset()
        instance_field = self._get_instance_filter_expr("pk", "in")

        instances_for_location = models.Instance.objects.filter(
            location__in=self.request.group.locations.all()
        )

        instances_for_service = InstanceService.objects.filter(
            service=self.request.group.service
        ).values("instance")

        instances_for_activation = self._instances_with_activation()

        return queryset.filter(
            Q(**{instance_field: instances_for_location})
            | Q(**{instance_field: instances_for_service})
            | Q(**{instance_field: instances_for_activation})
        )

    def get_queryset_for_service(self):
        queryset = self.get_base_queryset()
        instance_field = self._get_instance_filter_expr("pk", "in")
        instances = self._instances_with_activation()
        # use subquery to avoid duplicates
        return queryset.filter(**{instance_field: instances})

    def get_queryset_for_canton(self):
        return self.get_base_queryset()

    def _instances_with_activation(self):
        return Circulation.objects.filter(
            activations__service=self.request.group.service
        ).values("instance")


class InstanceEditableMixin(AttributeMixin):
    """Mixin to determine whether action is allowed on given instance.

    Define `instance_editable_permission` what permission is needed to edit.
    Currently there are `document` for attachments and `form` for form data.
    Set it to None if no specific permission is required.
    """

    def get_instance(self, obj):
        instance = obj
        instance_field = self.serializer_getattr("instance_field")
        if instance_field:
            instance = nested_getattr(obj, self.instance_field)

        return instance

    def has_editable_permission(self, instance):
        editable_permission = self.serializer_getattr("instance_editable_permission")
        return editable_permission is None or editable_permission in self.get_editable(
            instance
        )

    @permission_aware
    def get_editable(self, instance):
        # TODO: should be replaced with can-read and can-edit permissions
        # in form config. Difficulty is that documents are no real questions.

        editable = set()

        if instance.instance_state.name in ["Neu", "Zurückgewiesen", "new"]:
            return {"instance", "form", "document"}

        if instance.instance_state.name == "nfd":
            return {"document"}

        return editable

    def get_editable_for_service(self, instance):
        return {"form", "document"}

    def get_editable_for_municipality(self, instance):
        return {"form", "document"}

    def get_editable_for_canton(self, instance):
        return {"form", "document"}

    def get_editable_for_reader(self, instance):
        return set()

    def get_editable_for_public_reader(self, instance):
        return set()

    def has_object_update_permission(self, obj):
        instance = self.get_instance(obj)
        return self.has_editable_permission(instance)

    def has_object_destroy_permission(self, obj):
        return self.has_object_update_permission(obj)

    def _validate_instance_editablity(
        self, instance, is_editable_callable=lambda: True
    ):
        if not self.has_editable_permission(instance) or not is_editable_callable():
            raise exceptions.ValidationError(
                _("Not allowed to add data to instance %(instance)s")
                % {"instance": instance.pk}
            )

        return instance

    @permission_aware
    def validate_instance(self, instance):
        user = get_request(self).user
        return self._validate_instance_editablity(
            instance, lambda: instance.user == user
        )

    def validate_instance_for_municipality(self, instance):
        group = get_request(self).group
        service = group.service
        circulations = instance.circulations.all()

        return self._validate_instance_editablity(
            instance,
            lambda: group.locations.filter(pk=instance.location_id).exists()
            or circulations.filter(activations__service=service).exists()
            or InstanceService.objects.filter(
                service=service, instance=instance
            ).exists(),
        )

    def validate_instance_for_service(self, instance):
        service = get_request(self).group.service
        circulations = instance.circulations.all()

        return self._validate_instance_editablity(
            instance, lambda: circulations.filter(activations__service=service).exists()
        )

    def validate_instance_for_canton(self, instance):
        return self._validate_instance_editablity(instance)
