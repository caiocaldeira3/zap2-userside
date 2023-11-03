import dataclasses as dc
from datetime import datetime
from typing import Any

import pytz
from bson import ObjectId


@dc.dataclass()
class Message:
    message: str
    user_id: ObjectId
    time_sent: datetime = dc.field(default_factory=lambda: datetime.now(pytz.utc))

    def to_insert (self) -> dict[str, Any]:
        return {
            field.name: self.__getattribute__(field.name)
            for field in dc.fields(Message)
        }


@dc.dataclass()
class Chat:
    users: list[ObjectId]
    messages: list[Message] = dc.field(default_factory=list)
    name: str = dc.field(default="default chat")
    desc: str = dc.field(default="default desc")
    ctime: datetime = dc.field(default_factory=lambda: datetime.now(pytz.utc))
    mtime: datetime = dc.field(default_factory=lambda: datetime.now(pytz.utc))
    back_id: ObjectId = dc.field(default=None)
    _id: ObjectId = dc.field(default_factory=ObjectId)

    def __post_init__ (self) -> None:
        self.messages = [
            Message(**key) if not isinstance(key, Message) else key
            for key in self.messages
        ]

    def to_insert (self) -> dict[str, Any]:
        return {
            field.name: (
                self.__getattribute__(field.name)
                if field.name != "messages" else
                [ key.to_insert() for key in self.messages ]
            ) for field in dc.fields(Chat)
        }