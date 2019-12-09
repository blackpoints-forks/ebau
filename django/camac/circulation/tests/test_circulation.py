import pytest
from django.urls import reverse
from pytest_factoryboy import LazyFixture
from rest_framework import status

from camac.circulation import serializers


@pytest.mark.parametrize(
    "role__name,instance__user,num_queries",
    [
        ("Applicant", LazyFixture("admin_user"), 6),
        ("Canton", LazyFixture("user"), 6),
        ("Municipality", LazyFixture("user"), 6),
        ("Service", LazyFixture("user"), 6),
    ],
)
def test_circulation_list(
    admin_client,
    instance_state,
    circulation,
    activation,
    num_queries,
    django_assert_num_queries,
):
    url = reverse("circulation-list")

    included = serializers.CirculationSerializer.included_serializers
    with django_assert_num_queries(num_queries):
        response = admin_client.get(
            url,
            data={
                "instance_state": instance_state.pk,
                "include": ",".join(included.keys()),
            },
        )
    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert len(json["data"]) == 1
    assert json["data"][0]["id"] == str(circulation.pk)
    assert len(json["included"]) == len(included)


@pytest.mark.parametrize(
    "role__name,instance__user", [("Applicant", LazyFixture("admin_user"))]
)
def test_circulation_detail(admin_client, circulation):
    url = reverse("circulation-detail", args=[circulation.pk])

    response = admin_client.get(url)
    assert response.status_code == status.HTTP_200_OK
