from camac.constants.kt_bern import (
    SERVICE_GROUP_BAUKONTROLLE,
    SERVICE_GROUP_LEITBEHOERDE_GEMEINDE,
    SERVICE_GROUP_RSTA,
)
from camac.core.models import InstanceService
from camac.user.models import ServiceT


def get_baukontrolle(instance, active_service):
    """
    Find correct service for Baukontrolle.

    kt_bern specific.

    When switching to SB1, it's necessary to set baukontrolle as active service.
    """
    defining_leitbehoerde = active_service
    if active_service.service_group.pk == SERVICE_GROUP_RSTA:
        defining_leitbehoerde = instance.services.filter(
            service_group_id=SERVICE_GROUP_LEITBEHOERDE_GEMEINDE
        ).first()
    elif active_service.service_group.pk == SERVICE_GROUP_BAUKONTROLLE:
        return active_service

    service_t = ServiceT.objects.get(
        language="de", service=defining_leitbehoerde, service__disabled=0
    )
    city = service_t.name.replace("Leitbehörde ", "")
    return ServiceT.objects.get(language="de", name=f"Baukontrolle {city}").service


def set_baukontrolle(instance):
    """
    Switch active service to baukontrolle.

    kt_bern specific.

    When switching to SB1, it's necessary to set baukontrolle as active service.
    """
    active_service = instance.active_service
    baukontrolle = get_baukontrolle(instance, active_service)

    if baukontrolle != active_service:
        old_inst_serv = InstanceService.objects.get(
            service=active_service, instance=instance
        )
        old_inst_serv.active = 0
        old_inst_serv.save()

        InstanceService.objects.get_or_create(
            service=baukontrolle, instance=instance, defaults={"active": 1}
        )