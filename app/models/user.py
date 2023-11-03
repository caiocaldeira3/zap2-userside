import dataclasses as dc
from typing import Any

from bson import ObjectId


@dc.dataclass()
class User:
    name:str
    telephone: str
    password: str
    desc: str = dc.field(default="default description")
    _id: ObjectId = dc.field(default_factory=ObjectId)

    def to_insert (self) -> dict[str, Any]:
        return {
            field.name: self.__getattribute__(field.name)
            for field in dc.fields(User)
        }
