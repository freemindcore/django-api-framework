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
        generate_crud:      whether to create crud api, default to True
        model_exclude:      fields to be excluded in Schema, it will ignore model_fields
        model_fields:       fields to be included in Schema, default to "__all__"
        model_join:         prefetch and retrieve all m2m fields, default to False
        model_recursive:    recursively retrieve FK/OneToOne fields, default to False
        sensitive_fields:   fields to be ignored

    Example:
        class Meta
            model = Event
            generate_crud = False
            model_exclude = ["field1", "field2"]
            model_fields = ["field1", "field2"]
            model_join = False
            model_recursive = True
            sensitive_fields = ["token", "money"]
    """

    ...
