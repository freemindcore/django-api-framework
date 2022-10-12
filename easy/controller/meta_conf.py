from typing import Any, List, Optional, Type, Union

from django.db import models

META_ATTRIBUTE_NAME: str = "__EASY_API_META__"

GENERATE_CRUD_ATTR: str = "generate_crud"
GENERATE_CRUD_ATTR_DEFAULT = True

MODEL_EXCLUDE_ATTR: str = "model_exclude"
MODEL_EXCLUDE_ATTR_DEFAULT: List = []

MODEL_FIELDS_ATTR: str = "model_fields"
MODEL_FIELDS_ATTR_DEFAULT: str = "__all__"

MODEL_RECURSIVE_ATTR: str = "model_recursive"
MODEL_RECURSIVE_ATTR_DEFAULT: bool = False

MODEL_JOIN_ATTR: str = "model_join"
MODEL_JOIN_ATTR_DEFAULT: bool = False

SENSITIVE_FIELDS_ATTR: str = "sensitive_fields"
SENSITIVE_FIELDS_ATTR_DEFAULT: List = ["password", "token"]


class ModelOptions:
    def __init__(self, options: object = None):
        """
        Configuration reader
        """
        self.model: Optional[Type[models.Model]] = getattr(options, "model", None)
        self.generate_crud: Optional[Union[bool]] = getattr(
            options, GENERATE_CRUD_ATTR, GENERATE_CRUD_ATTR_DEFAULT
        )
        self.model_exclude: Union[Union[str], List[Any]] = getattr(
            options, MODEL_EXCLUDE_ATTR, MODEL_EXCLUDE_ATTR_DEFAULT
        )
        self.model_fields: Union[Union[str], List[Any]] = getattr(
            options, MODEL_FIELDS_ATTR, MODEL_FIELDS_ATTR_DEFAULT
        )
        self.model_join: Optional[Union[bool]] = getattr(
            options, MODEL_JOIN_ATTR, MODEL_JOIN_ATTR_DEFAULT
        )
        self.model_recursive: Optional[Union[bool]] = getattr(
            options, MODEL_RECURSIVE_ATTR, MODEL_RECURSIVE_ATTR_DEFAULT
        )
        self.sensitive_fields: Optional[Union[str, List[str]]] = getattr(
            options, SENSITIVE_FIELDS_ATTR, list(SENSITIVE_FIELDS_ATTR_DEFAULT)
        )

    @classmethod
    def get_model_options(cls, klass: Type) -> Any:
        return ModelOptions(getattr(klass, "Meta", None))

    @classmethod
    def set_model_meta(
        cls, model: Type[models.Model], model_opts: "ModelOptions"
    ) -> None:
        setattr(
            model,
            META_ATTRIBUTE_NAME,
            {
                GENERATE_CRUD_ATTR: model_opts.generate_crud,
                MODEL_EXCLUDE_ATTR: model_opts.model_exclude,
                MODEL_FIELDS_ATTR: model_opts.model_fields,
                MODEL_RECURSIVE_ATTR: model_opts.model_recursive,
                MODEL_JOIN_ATTR: model_opts.model_join,
                SENSITIVE_FIELDS_ATTR: model_opts.sensitive_fields,
            },
        )


class ModelMetaConfig(object):
    @staticmethod
    def get_configuration(obj: models.Model, _name: str, default: Any = None) -> Any:
        _value = default if default else None
        if hasattr(obj, META_ATTRIBUTE_NAME):
            _value = getattr(obj, META_ATTRIBUTE_NAME).get(_name, _value)
        return _value

    def get_model_recursive(self, obj: models.Model) -> bool:
        model_recursive: bool = self.get_configuration(
            obj, MODEL_RECURSIVE_ATTR, default=MODEL_RECURSIVE_ATTR_DEFAULT
        )
        return model_recursive

    def get_model_join(self, obj: models.Model) -> bool:
        model_join: bool = self.get_configuration(
            obj, MODEL_JOIN_ATTR, default=MODEL_JOIN_ATTR_DEFAULT
        )
        return model_join

    def get_model_fields_list(self, obj: models.Model) -> List[Any]:
        model_fields: List = self.get_configuration(
            obj, MODEL_FIELDS_ATTR, default=MODEL_FIELDS_ATTR_DEFAULT
        )
        return model_fields

    def get_model_exclude_list(self, obj: models.Model) -> List[Any]:
        exclude_list: List = self.get_configuration(
            obj, MODEL_EXCLUDE_ATTR, default=MODEL_EXCLUDE_ATTR_DEFAULT
        )
        return exclude_list

    def get_sensitive_list(self, obj: models.Model) -> List[Any]:
        sensitive_list: List = self.get_configuration(
            obj, SENSITIVE_FIELDS_ATTR, default=SENSITIVE_FIELDS_ATTR_DEFAULT
        )
        return sensitive_list

    def get_final_excluded_list(self, obj: models.Model) -> List[Any]:
        total_excluded_list = []
        sensitive_list: List = list(SENSITIVE_FIELDS_ATTR_DEFAULT)
        excluded_list = []

        sensitive_fields = self.get_sensitive_list(obj)
        if sensitive_fields:
            sensitive_list.extend(sensitive_fields)
        sensitive_list = list(set(sensitive_list))

        excluded_fields = self.get_model_exclude_list(obj)
        if excluded_fields:
            excluded_list.extend(excluded_fields)
        excluded_list = list(set(excluded_list))

        total_excluded_list.extend(sensitive_list)
        total_excluded_list.extend(excluded_list)
        return list(set(total_excluded_list))

    def show_field(self, obj: models.Model, field_name: str) -> bool:
        model_exclude_list = self.get_model_exclude_list(obj)
        if model_exclude_list:
            if field_name in self.get_final_excluded_list(obj):
                return False
        else:
            if field_name in self.get_final_excluded_list(obj):
                return False
            model_fields_list = self.get_model_fields_list(obj)
            if model_fields_list != MODEL_FIELDS_ATTR_DEFAULT:
                if field_name not in model_fields_list:
                    return False
        return True
