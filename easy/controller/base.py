import logging

from easy.controller.meta import CrudApiMetaclass

logger = logging.getLogger(__name__)


class CrudAPIController(metaclass=CrudApiMetaclass):
    """
    Base APIController for auto creating CRUD APIs, configurable via Meta class
    APIs auto generated:
        Creat
            PUT /{id}       - Create a single Object

        Read
            GET /{id}       - Retrieve a single Object
            GET /           - Retrieve multiple Object, paginated, support filtering

        Update
            PATCH /{id}     - Update a single Object

        Delete
            DELETE /{id}    - Delete a single Object

    Configuration:
        model:              django model
        model_fields:       fields to be included in Schema, default to "__all__"
        model_exclude:      fields to be excluded in Schema
        model_join:         retrieve all m2m fields, default to True
        model_recursive:    recursively retrieve FK/OneToOne models, default to False
        sensitive_fields:   fields to be ignored
    """

    ...
