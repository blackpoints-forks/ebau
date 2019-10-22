from django.conf import settings

from ..caluma import CalumaClient


def query_from_file(file_name):
    with open(file_name, "r") as myfile:
        data = myfile.read()
    return data


class DocumentParser:
    def __init__(self, document: dict):
        self.document = document
        self.answers = self.parse_answers(self.document)
        self.answers["form-name"] = document["form"]["name"]

    def parse_answers(self, data):
        answers = {}
        simple_questions = {
            "IntegerQuestion": "integerValue",
            "FloatQuestion": "floatValue",
            "TextQuestion": "stringValue",
            "TextareaQuestion": "stringValue",
            "DateQuestion": "dateValue",
        }
        choice_questions = {
            "ChoiceQuestion": "choiceOptions",
            "MultipleChoiceQuestion": "multipleChoiceOptions",
            "DynamicChoiceQuestion": "dynamicChoiceOptions",
            "DynamicMultipleChoiceQuestion": "dynamicMultipleChoiceOptions",
        }

        for answer in data["answers"]["edges"]:
            question_type_name = answer["node"]["question"]["__typename"]

            if question_type_name in simple_questions:
                answers[answer["node"]["question"]["slug"]] = answer["node"][
                    simple_questions[question_type_name]
                ]

            elif question_type_name in choice_questions:
                options = {
                    option["node"]["slug"]: option["node"]["label"]
                    for option in answer["node"]["question"][
                        choice_questions[question_type_name]
                    ]["edges"]
                }

                if question_type_name in ["ChoiceQuestion", "DynamicChoiceQuestion"]:
                    answers[answer["node"]["question"]["slug"]] = options[
                        answer["node"]["stringValue"]
                    ]

                elif question_type_name in [
                    "MultipleChoiceQuestion",
                    "DynamicMultipleChoiceQuestion",
                ]:
                    answers[answer["node"]["question"]["slug"]] = [
                        options[slug] for slug in answer["node"]["listValue"]
                    ]
            elif question_type_name == "TableQuestion":
                rows = []
                for table_value in answer["node"]["tableValue"]:
                    rows.append(self.parse_answers(table_value))
                answers[answer["node"]["question"]["slug"]] = rows

        return answers


def get_document(instance_id, auth_header, group_pk):
    filter = {"filter": [{"key": "camac-instance-id", "value": instance_id}]}
    caluma = CalumaClient(auth_header)

    resp = caluma.query_caluma(
        query_from_file(
            str(settings.ROOT_DIR("camac/echbern/gql/get_document.graphql"))
        ),
        variables=filter,
        add_headers={"X-CAMAC-GROUP": str(group_pk)},
    )
    dp = DocumentParser(resp["data"]["allDocuments"]["edges"][0]["node"])
    return dp.answers