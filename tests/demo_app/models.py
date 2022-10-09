from django.db import models


class TestBaseModel(models.Model):
    class Meta:
        app_label = "demo_app"
        abstract = True


class Category(TestBaseModel):
    title = models.CharField(max_length=100)
    status = models.PositiveSmallIntegerField(default=1, null=True)


class Client(TestBaseModel):
    key = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    password = models.CharField(max_length=30, null=True)


class Type(TestBaseModel):
    name = models.CharField(max_length=50, null=True)
    status = models.PositiveSmallIntegerField(default=1, null=True)


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
    photo = models.ImageField(upload_to="client/photo", null=True)

    owner = models.ManyToManyField(to=Client, related_name="events", null=True)

    lead_owner = models.ManyToManyField(to=Client, related_name="lead_owner", null=True)

    type = models.ForeignKey(Type, on_delete=models.CASCADE, null=True)

    sensitive_info = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.title
