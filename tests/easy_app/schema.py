from datetime import date

from ninja import Schema


class EventSchema(Schema):
    title: str
    start_date: date
    end_date: date

    class Config:
        orm_mode = True


class EventSchemaOut(Schema):
    id: int
