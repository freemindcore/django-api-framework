![Test](https://github.com/freemindcore/django-api-framework/actions/workflows/test_full.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-api-framework.svg)](https://badge.fury.io/py/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/v/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/pyversions/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/djversions/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![Codecov](https://img.shields.io/codecov/c/gh/freemindcore/django-api-framework)](https://codecov.io/gh/freemindcore/django-api-framework)
[![Downloads](https://pepy.tech/badge/django-api-framework/month)](https://pepy.tech/project/django-api-framework)

# Django Easy API Framework

###  Easy and Fast Django REST framework based on Django-Ninja-Extra

- CRUD Async API Generation: Automatic and configurable, inspired by [NextJs-Crud](https://github.com/nestjsx/crud).
- Domain/Service/Controller Base Structure: for better code organization.
- Base Permission/Response/Exception Classes: and many handy features to help your API coding easier
- Pure class based [Django-Ninja](https://github.com/vitalik/django-ninja) APIs: thanks to [Django-Ninja-Extra](https://github.com/eadwinCode/django-ninja-extra)

```
Django-Ninja features:

  Easy: Designed to be easy to use and intuitive.
  FAST execution: Very high performance thanks to Pydantic and async support.
  Fast to code: Type hints and automatic docs lets you focus only on business logic.
  Standards-based: Based on the open standards for APIs: OpenAPI (previously known as Swagger) and JSON Schema.
  Django friendly: (obviously) has good integration with the Django core and ORM.

Plus Extra:
  Class Based: Design your APIs in a class based fashion.
  Permissions: Protect endpoint(s) at ease with defined permissions and authorizations at route level or controller level.
  Dependency Injection: Controller classes supports dependency injection with python Injector or django_injector. Giving you the ability to inject API dependable services to APIController class and utilizing them where needed
```

### Requirements
- Python >= 3.6
- Django >= 3.1
- pydantic >= 1.6
- Django-Ninja-extra >= 0.15.0

### Install
`pip install django-api-framework`

Then add "easy" to your django INSTALLED_APPS:

```
[
    ...,
    "easy",
    ...,
]
```

### Usage
#### Get all your Django app CRUD APIs up and running
In your Django project next to urls.py create new apis.py file:
```
from easy.main import EasyAPI

api_admin_v1 = EasyAPI(
    urls_namespace="admin_api",
    version="v1.0.0",
)

# Automatic Admin API generation
api_admin_v1.auto_create_admin_controllers()
```
Now go to urls.py and add the following:
```
from django.urls import path
from .apis import api_admin_v1

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api_admin/v1/", api_admin_v1.urls),  # <---------- !
]
```
Now go to http://127.0.0.1:8000/api_admin/v1/docs

You will see the automatic interactive API documentation (provided by Swagger UI).
![Auto generated APIs List](https://github.com/freemindcore/django-api-framework/blob/fae8209a8d08c55daf75ac3a4619fe62b8ef3af6/docs/images/admin_apis_list.png)

#### Adding CRUD APIs to a specific API Controller

By inheriting CrudAPIController class, CRUD APIs will be added to your API controller.
Configuration is available via Meta class:
- `model_exclude`:      fields to be excluded in Schema
- `model_fields`:       fields to be included in Schema, default to `"__all__"`
- `model_join`:         prefetch and retrieve all m2m fields, default to False
- `model_recursive`:    recursively retrieve FK/OneToOne fields, default to False
- `sensitive_fields`:   fields to be ignored


Example:
```
@api_controller("even_api", permissions=[AdminSitePermission])
class EventAPIController(CrudAPIController):
    def __init__(self, service: EventService):
        super().__init__(service)

    class Meta:
        model = Event # django model
        generate_crud = True # whether to create crud api, default to True
        model_fields = ["field_1", "field_2",] # if not configured default to "__all__"
        model_join = True
        model_recursive = True
        sensitive_fields = ["password", "sensitive_info"]

```
Please check tests/demo_app for more examples.


### Boilerplate Django project
A boilerplate Django project for quickly getting started, production ready easy-apis wiht 100% test coverage ready:
https://github.com/freemindcore/django-easy-api

![Auto generated APIs - Users](https://github.com/freemindcore/django-api-framework/blob/9aa26e92b6fd79f4d9db422ec450fe62d4cd97b9/docs/images/user_admin_api.png)
![Auto generated APIs - Schema](https://github.com/freemindcore/django-api-framework/blob/9aa26e92b6fd79f4d9db422ec450fe62d4cd97b9/docs/images/auto_api_demo_2.png)

### Thanks to your help
**_If you find this project useful, please give your stars to support this open-source project. :) Thank you !_**
