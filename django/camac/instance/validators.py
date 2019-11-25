import itertools
import locale
import sys
from functools import partial

import inflection
from django.conf import settings
from django.utils.translation import gettext as _
from pyjexl.jexl import JEXL
from pyproj import CRS, Transformer
from rest_framework import exceptions

from camac.document.models import Attachment
from camac.jexl import ExtractTransformSubjectAnalyzer

from . import models

locale.setlocale(locale.LC_ALL, f"{settings.LOCALE_NAME}.UTF-8")


class FormDataValidator(object):
    def __init__(self, instance):
        self.forms_def = settings.FORM_CONFIG
        self.instance = instance
        self.fields = {
            **{
                field.name: field.value
                for field in models.FormField.objects.filter(instance=instance)
            },
            # handle attachments like fields
            **{
                attachment.question: attachment.path
                for attachment in Attachment.objects.filter(instance=instance)
            },
        }
        self.jexl = JEXL()
        self.jexl.add_transform("value", lambda name: self.fields.get(name))
        self.jexl.add_transform("mapby", lambda arr, key: [obj[key] for obj in arr])
        self.active_question_cache = {}

    def _validate_question_radio(self, question, question_def, value):
        if value not in question_def["config"]["options"]:
            raise exceptions.ValidationError(
                _("Invalid value `%(value)s` in field `%(field)s`")
                % {"value": value, "field": question}
            )

    def _validate_question_checkbox(self, question, question_def, value):
        options = set(question_def["config"]["options"])
        # avoid `TypeError` as value may be None

        values = set(value or [None])
        diff = values - options

        if diff:
            raise exceptions.ValidationError(
                _("Invalid values `%(values)s` in field `%(field)s`")
                % {"values": ", ".join([str(val) for val in diff]), "field": question}
            )

    def _validate_question_text(self, question, question_def, value):
        if not isinstance(value, str) or not value:
            raise exceptions.ValidationError(
                _("Value of field `%(field)s` must be `str` and not empty")
                % {"field": question}
            )

    def _validate_question_textarea(self, question, question_def, value):
        self._validate_question_text(question, question_def, value)

    def _validate_question_date(self, question, question_def, value):
        # TODO: Needs to properly validate a date input, once the frontend validates this too
        self._validate_question_text(question, question_def, value)

    def _validate_question_number(self, question, question_def, value):
        min_val = question_def["config"].get("min", -sys.maxsize - 1)
        max_val = question_def["config"].get("max", sys.maxsize)

        if (
            not isinstance(value, int)
            and not isinstance(value, float)
            or value < min_val
            or value > max_val
        ):
            raise exceptions.ValidationError(
                _(
                    "Value of field `%(field)s` needs to be a number "
                    "between %(min_val)s and %(max_val)s)."
                )
                % {"field": question, "min_val": min_val, "max_val": max_val}
            )

    def _validate_question_number_separator(self, question, question_def, value):
        self._validate_question_number(question, question_def, value)

    def _validate_question_document(self, question, question_def, value):
        if not value:
            raise exceptions.ValidationError(
                _("Document missing for question `%(field)s") % {"field": question}
            )

    def _validate_question_gwr(self, question, question_def, value):
        # TODO: might be better generic table with a gwr config option
        self._validate_question_table(question, question_def, value)

    def _validate_question_table(self, question, question_def, value):
        columns = question_def["config"]["columns"]
        for row in list(value or [{}]):
            if not isinstance(row, list):
                row = [row]

            for row_object in row:
                for column in columns:
                    self._validate_question(
                        "{0}/{1}".format(question, column["name"]),
                        column,
                        row_object.get(column["name"]),
                    )

    def _check_questions_active(self, questions):
        for question in questions:
            if not self._check_question_active(
                question, self.forms_def["questions"][question]
            ):
                return False

        return True

    def _check_question_active(self, question, question_def):
        """Question is only active when all dependend questions are active as well."""

        if question in self.active_question_cache:
            return self.active_question_cache[question]

        expression = question_def.get("active-expression")
        if expression is None:
            return True

        dep_questions = self.jexl.analyze(
            expression, partial(ExtractTransformSubjectAnalyzer, transforms=["value"])
        )
        active = False
        try:
            active = (
                expression is None
                or self._check_questions_active(dep_questions)
                and self.jexl.evaluate(expression, {"form": self.instance.form.name})
            )
        except TypeError:
            # A TypeError is raised if a question is not filled. It then tries
            # to e.g compare None < 250 which can't work
            pass

        self.active_question_cache[question] = active
        return active

    def _check_question_required(self, question, question_def):
        if not question_def["required"]:
            return False

        return self._check_question_active(question, question_def)

    def _validate_question(self, question, question_def, value):
        required = self._check_question_required(question, question_def)

        # do not validate optional fields without a value
        if not required and not value:
            return

        validate_method = getattr(
            self,
            "_validate_question_{0}".format(
                inflection.underscore(question_def["type"])
            ),
        )
        validate_method(question, question_def, value)

    def validate(self):
        form_def = self.get_form_def(self.instance.form.name)
        questions = itertools.chain(
            *[self.forms_def["modules"][module]["questions"] for module in form_def]
        )

        for question in questions:
            value = self.fields.get(question)
            self._validate_question(
                question, self.forms_def["questions"][question], value
            )

    def get_form_def(self, form_name):
        form_def = self.forms_def["forms"].get(form_name)

        if form_def is None:
            raise exceptions.ValidationError(
                _("Invalid form type %(form)s.") % {"form": form_name}
            )

        return form_def

    def get_active_modules_questions(self):  # noqa: C901
        COORDINATE_QUESTION = "punkte"
        DOCUMENT_TYPE = "document"
        IGNORED_MODULE = "freigegebene-unterlagen"
        form_def = self.get_form_def(self.instance.form.name)
        relevant_data = []
        signature = {"slug": "signature", "title": "Unterschriften", "people": {}}

        for module_name in form_def:
            if module_name == IGNORED_MODULE:
                continue

            active_questions = []
            module = self.forms_def["modules"][module_name]

            for question_name in module["questions"]:
                if (
                    not question_name == "layer"
                    and not question_name.split("-")[0] == "info"
                ):
                    question = self.forms_def["questions"][question_name]

                    if self._check_question_active(question_name, question):
                        value = self.fields.get(question_name)
                        label = question["label"]
                        type = question["type"]

                        if question_name == COORDINATE_QUESTION and value is not None:
                            """
                            This converts the coordinates of the set points on the GIS map from
                            GPS(EPSG:4326) coordinates to the coordinate system Schwyz uses
                            """
                            converted_values = []
                            transformer = Transformer.from_crs(
                                "EPSG:4326",
                                CRS.from_proj4(
                                    "+proj=somerc +lat_0=46.95240555555556 +lon_0=7.439583333333333 +k_0=1 +x_0=2600000 +y_0=1200000 +ellps=bessel +towgs84=674.374,15.056,405.346,0,0,0,0 +units=m +no_defs"
                                ),
                            )

                            for coord_set in value:
                                if not isinstance(coord_set, list):
                                    coord_set = [coord_set]
                                for coord in coord_set:
                                    lat, lng = transformer.transform(
                                        coord["lat"], coord["lng"]
                                    )
                                    converted_values.append(
                                        f"{int(float(lat)):n} / {int(float(lng)):n}"
                                    )

                            value = converted_values
                            label = "Koordinaten"
                            type = "coordinates"
                        elif type == DOCUMENT_TYPE and value is not None:
                            value = value.name.split("/")[-1]

                        active_questions.append(
                            {
                                "label": label,
                                "type": type,
                                "value": value,
                                "config": question["config"],
                            }
                        )

            if module["parent"] is None:
                relevant_data.append(
                    {
                        "slug": module_name,
                        "title": module["title"],
                        "subModules": [],
                        "questions": active_questions,
                    }
                )
            else:
                parent = next(
                    item for item in relevant_data if item["slug"] == module["parent"]
                )

                parent["subModules"].append(
                    {
                        "slug": module_name,
                        "title": module["title"],
                        "questions": active_questions,
                    }
                )

            if module["parent"] == "personalien":
                for question in active_questions:
                    names = []
                    split_names = []

                    if question["value"] is not None:
                        for value in question["value"]:
                            firma = value["firma"] + "\n" if "firma" in value else ""
                            names.append(
                                f"{firma}{value.get('name', '')} {value.get('vorname', '')}"
                            )

                    # split people into arrays of 3
                    for i in range(0, len(names), 3):
                        split_names.append(names[i : i + 3])

                    signature["people"][question["label"]] = split_names

        # sort signature categories alphabetically
        sorted_signature = {}
        for key, value in sorted(signature["people"].items()):
            sorted_signature[key] = value
        signature["people"] = sorted_signature

        relevant_data.append(signature)

        return relevant_data
