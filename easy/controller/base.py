import logging

from ninja_extra import ControllerBase

from easy.controller.meta import CrudAPI, CrudApiMetaclass

logger = logging.getLogger(__name__)


class CrudAPIController(ControllerBase, CrudAPI, metaclass=CrudApiMetaclass):
    """
    Base APIController for auto creating CRUD APIs

    GET /{id}       - Retrieve a single Object
    PUT /           -  Create a single Object
    PATCH /?id={id} - Update a single field for a Object
    DELETE /{id}    - Delete a single Object
    GET /get_all    - Retrieve multiple Object
    GET /filter/?filters={filters_dict}
                    - Filter Objects with django-orm filter dict
    GET /filter_exclude/?filters={filters_dict}
                    - Filter exclude Objects with Django-ORM filter dict

    """

    ...
