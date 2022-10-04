from easy.domain import BaseDomain
from tests.demo_app.models import Event


class EventDomain(BaseDomain):
    pass


class EventBiz(EventDomain):
    def __init__(self, model=Event):
        self.model = model
        super(EventBiz, self).__init__(self.model)
