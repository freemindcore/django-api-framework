from abc import abstractmethod
from typing import Any, Dict, Optional


class CrudModel(object):
    APIMeta: Dict = {}

    def __init__(self, model: Any):
        self.model = model

    @abstractmethod
    def crud_add_obj(self, **payload: Dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_del_obj(self, pk: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def crud_update_obj(self, pk: int, payload: Dict) -> bool:
        raise NotImplementedError

    @abstractmethod
    def crud_get_obj(self, pk: int) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_get_objs_all(self, maximum: Optional[int] = None, **filters: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_filter(self, **kwargs: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def crud_filter_exclude(self, **kwargs: Any) -> Any:
        raise NotImplementedError
