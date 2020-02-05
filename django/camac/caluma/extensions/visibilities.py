import json.decoder

import requests
from caluma.caluma_core.visibilities import BaseVisibility, filter_queryset_for
from caluma.caluma_form import models as form_models, schema as form_schema
from django.conf import settings
from django.db.models import F, Q

from camac.constants.kt_bern import DASHBOARD_FORM_SLUG
from camac.utils import build_url, filters, headers


class CustomVisibility(BaseVisibility):
    """Custom visibility for Kanton Bern.

    This defers the visibility to CAMAC-NG, by querying the NG API for all
    visible instances for the given user.

    Note: This expects that each document has a meta property that stores the
    CAMAC instance identifier, named "camac-instance-id". Each node is
    filtered by indirectly looking for the value of said property.

    To avoid multiple lookups to the Camac-NG API, the result is cached in the
    request object, and resused if the need arises. Caching beyond a request is
    not done but might become a future optimisation.
    """

    def get_unlinked_table_documents_filter(self, info, prefix=""):
        """Get filterset for unlinked table documents.

        An document can be identified as unlinked table document if it is a
        root level document (pk is the same as the family) and if if doesn't
        have a camac-instance-id assigned. For those documents to be visible,
        they also need to be created by the requester.
        """
        return {
            f"{prefix}meta__camac-instance-id__isnull": True,
            f"{prefix}family": F("pk"),
            f"{prefix}created_by_user": info.context.user.userinfo["sub"],
        }

    @filter_queryset_for(form_schema.Document)
    def filter_queryset_for_document(self, node, queryset, info):
        return queryset.filter(
            Q(form__slug=DASHBOARD_FORM_SLUG)
            | Q(family__in=self._all_visible_documents(info))
            | Q(**self.get_unlinked_table_documents_filter(info))
        )

    @filter_queryset_for(form_schema.Answer)
    def filter_queryset_for_answer(self, node, queryset, info):
        return queryset.filter(
            Q(document__form__slug=DASHBOARD_FORM_SLUG)
            | Q(document__family__in=self._all_visible_documents(info))
            | Q(**self.get_unlinked_table_documents_filter(info, prefix="document__"))
        )

    def _all_visible_documents(self, info):
        """Fetch all visible caluma documents and cache the result."""

        result = getattr(info.context, "_visibility_documents_cache", None)
        if result is not None:
            return result

        document_ids = form_models.Document.objects.filter(
            **{"meta__camac-instance-id__in": self._all_visible_instances(info)}
        ).values_list("pk", flat=True)

        setattr(info.context, "_visibility_documents_cache", document_ids)

        return document_ids

    def _all_visible_instances(self, info):
        """Fetch visible camac instances from NG API, caches the result.

        Take user's group from a custom HTTP header named `X-CAMAC-GROUP`
        which is then forwarded as a filter to the NG API to retrieve all
        Camac instance IDs that are accessible.

        Return a list of instance identifiers.
        """
        result = getattr(info.context, "_visibility_instances_cache", None)
        if result is not None:
            return result

        resp = requests.get(
            build_url(settings.INTERNAL_BASE_URL, "/api/v1/instances"),
            # forward filters via query params
            {**filters(info), "fields[instances]": "id"},
            headers=headers(info),
        )

        try:
            jsondata = resp.json()
            if "error" in jsondata:
                # forward Instance API error to client
                raise RuntimeError("Error from NG API: %s" % jsondata["error"])

            instance_ids = [int(rec["id"]) for rec in jsondata["data"]]
            setattr(info.context, "_visibility_instances_cache", instance_ids)

            return getattr(info.context, "_visibility_instances_cache")

        except json.decoder.JSONDecodeError:
            raise RuntimeError("NG API returned non-JSON response, check configuration")

        except KeyError:
            raise RuntimeError(
                f"NG API returned unexpected data structure (no data key): {jsondata}"
            )