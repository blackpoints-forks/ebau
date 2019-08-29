from django_filters.filters import BaseCSVFilter
from django_filters.rest_framework import DateTimeFilter, FilterSet

from camac.filters import CharMultiValueFilter, NumberFilter

from . import models


class AttachmentFilterSet(FilterSet):
    name = CharMultiValueFilter(lookup_expr="startswith")

    class Meta:
        model = models.Attachment
        fields = ("instance", "user", "name", "attachment_sections")


class AttachmentDownloadFilterSet(FilterSet):
    attachments = BaseCSVFilter(field_name="pk", method="filter_attachments")

    def filter_attachments(self, queryset, name, value):
        return queryset.filter(pk__in=value)

    class Meta:
        model = models.Attachment
        fields = ("attachments",)


class TemplateFilterSet(FilterSet):
    global_template = NumberFilter(field_name="group", lookup_expr="isnull")

    class Meta:
        model = models.Template
        fields = ("global_template",)


class AttachmentDownloadHistoryFilterSet(FilterSet):
    name = CharMultiValueFilter(lookup_expr="startswith")
    download_date_after = DateTimeFilter(field_name="date_time", lookup_expr="gte")
    download_date_before = DateTimeFilter(field_name="date_time", lookup_expr="lte")

    class Meta:
        model = models.AttachmentDownloadHistory
        fields = (
            "date_time",
            "keycloak_id",
            "name",
            "attachment",
            "group",
            "group__role",
        )
