from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from . import models


class ServiceGroupFactory(DjangoModelFactory):
    name = Faker('uuid4')

    class Meta:
        model = models.ServiceGroup


class ServiceFactory(DjangoModelFactory):
    name = Faker('uuid4')
    sort = 0
    service_group = SubFactory(ServiceGroupFactory)

    class Meta:
        model = models.Service


class UserFactory(DjangoModelFactory):
    name = Faker('name')
    username = Faker('uuid4')
    disabled = 0
    language = 'de'

    class Meta:
        model = models.User


class RoleFactory(DjangoModelFactory):
    name = Faker('name')

    class Meta:
        model = models.Role


class GroupFactory(DjangoModelFactory):
    name = Faker('name')
    role = SubFactory(RoleFactory)
    service = SubFactory(ServiceFactory)

    class Meta:
        model = models.Group


class UserGroupFactory(DjangoModelFactory):
    user = SubFactory(UserFactory)
    group = SubFactory(GroupFactory)
    default_group = 0

    class Meta:
        model = models.UserGroup


class LocationFactory(DjangoModelFactory):
    name = Faker('city')

    class Meta:
        model = models.Location


class GroupLocationFactory(DjangoModelFactory):
    group = SubFactory(GroupFactory)
    location = SubFactory(LocationFactory)

    class Meta:
        model = models.GroupLocation
