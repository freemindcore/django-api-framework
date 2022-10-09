import logging

from ninja_extra import ControllerBase

from easy.controller.meta import CrudAPI, CrudApiMetaclass

logger = logging.getLogger(__name__)


class CrudAPIController(ControllerBase, CrudAPI, metaclass=CrudApiMetaclass):
    """
    Base APIController for auto creating CRUD APIs

    GET /{id}       - Retrieve a single Object
    PUT /{id}               - Create a single Object
    PATCH /{id}     - Update fields for an Object
    DELETE /{id}    - Delete a single Object
    GET /           - Retrieve multiple Object, paginated
    """

    ...
