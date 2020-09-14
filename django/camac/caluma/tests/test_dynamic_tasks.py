import pytest
from caluma.caluma_form.models import Form
from caluma.caluma_workflow.api import skip_work_item, start_case
from caluma.caluma_workflow.models import Case, Workflow

from camac.constants.kt_bern import (
    DECISIONS_ABGELEHNT,
    DECISIONS_ABGESCHRIEBEN,
    DECISIONS_BEWILLIGT,
)


@pytest.mark.parametrize(
    "decision,expected_case_status",
    [
        (DECISIONS_ABGELEHNT, Case.STATUS_COMPLETED),
        (DECISIONS_ABGESCHRIEBEN, Case.STATUS_COMPLETED),
        (DECISIONS_BEWILLIGT, Case.STATUS_RUNNING),
    ],
)
def test_dynamic_task_after_decision(
    db,
    caluma_admin_user,
    caluma_workflow_config_be,
    docx_decision_factory,
    instance,
    decision,
    expected_case_status,
):
    docx_decision_factory(decision=decision, instance=instance.pk)

    case = start_case(
        workflow=Workflow.objects.get(pk="building-permit"),
        form=Form.objects.get(pk="main-form"),
        user=caluma_admin_user,
        meta={"camac-instance-id": instance.pk},
    )

    for task_id in [
        "submit",
        "ebau-number",
        "init-circulation",
        "circulation",
        "start-decision",
        "decision",
    ]:
        skip_work_item(case.work_items.get(task_id=task_id), caluma_admin_user)

    case.refresh_from_db()

    assert case.status == expected_case_status

    if case.status == Case.STATUS_RUNNING:
        assert case.work_items.filter(task_id="sb1").exists()
