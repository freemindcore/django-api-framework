from django.db import models


class TestBaseModel(models.Model):
    class Meta:
        app_label = "demo_app"
        abstract = True


class Category(TestBaseModel):
    title = models.CharField(max_length=100)


class Event(TestBaseModel):
    title = models.CharField(max_length=100)
    category = models.OneToOneField(
        Category, null=True, blank=True, on_delete=models.SET_NULL
    )
    start_date = models.DateField(
        null=True,
    )
    end_date = models.DateField(
        null=True,
    )

    def __str__(self):
        return self.title


class Client(TestBaseModel):
    key = models.CharField(max_length=20, unique=True)
