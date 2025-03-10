from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone


@pytest.mark.parametrize("instance_state__name", ["circulation"])
def test_send_inquiry_reminders(
    db,
    be_instance,
    active_inquiry_factory,
    notification_template,
    system_operation_user,
    mailoutbox,
    mocker,
):
    mocker.patch(
        "camac.notification.management.commands.send_inquiry_reminders.TEMPLATE_REMINDER_CIRCULATION",
        notification_template.slug,
    )

    active_inquiry_factory(deadline=timezone.now() - timedelta(days=1))

    call_command("send_inquiry_reminders")
    assert len(mailoutbox) == 1
