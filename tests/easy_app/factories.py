from django.contrib.auth import get_user_model
from factory import Faker
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):

    username = Faker("user_name")
    email = Faker("email")

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]
