![Test](https://github.com/freemindcore/django-api-framework/actions/workflows/test_full.yml/badge.svg)
[![PyPI version](https://badge.fury.io/py/django-api-framework.svg)](https://badge.fury.io/py/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/v/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/pyversions/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![PyPI version](https://img.shields.io/pypi/djversions/django-api-framework.svg)](https://pypi.python.org/pypi/django-api-framework)
[![Codecov](https://img.shields.io/codecov/c/gh/freemindcore/django-api-framework)](https://codecov.io/gh/freemindcore/django-api-framework)
[![Downloads](https://pepy.tech/badge/django-api-framework/month)](https://pepy.tech/project/django-api-framework)

# Django Easy API Framework

###  Easy and Fast Django REST framework based on Django-ninja-extra

- Auto CRUD Async API generation for all django models, configurable via Meta class
- Domain/Service/Controller base structure for better code organization
- Base Permission/Response/Exception classes and more to come
- Pure class based [Django-Ninja](https://github.com/vitalik/django-ninja) APIs, based on [Django-Ninja-extra](https://github.com/eadwinCode/django-ninja-extra)

```
Django-Ninja features :

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


Get your admin api up and running:
```
api_admin_v1 = EasyAPI(
    urls_namespace="admin_api",
    version="v1.0.0",
)

# Automatic Admin API generation
api_admin_v1.auto_create_admin_controllers()
```

Please check tests/demo_app for more.


### Boilerplate Django project
A boilerplate Django project for quickly getting started:
https://github.com/freemindcore/django-easy-api

![Auto generated APIs List](https://github.com/freemindcore/django-api-framework/blob/fae8209a8d08c55daf75ac3a4619fe62b8ef3af6/docs/images/admin_apis_list.png)
![Auto generated APIs - Users](https://github.com/freemindcore/django-api-framework/blob/fae8209a8d08c55daf75ac3a4619fe62b8ef3af6/docs/images/user_admin_api.png)

_Note: this project is still in early stage, comments and advices are highly appreciated._
