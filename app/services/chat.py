from bson import ObjectId

from app.models.chat import Chat, Message
from app.util import config, mongodb


def find_with_id (chat_id: ObjectId) -> Chat:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "chat")
    if not isinstance(chat_id, ObjectId):
        chat_id = ObjectId(chat_id)

    result = mdb.find_one({ "_id": chat_id })
    if result is None:
        raise None

    result["messages"] = [
        Message(**key) for key in result.get("messages", ())
    ]

    return Chat(**result)

def insert_chat (chat: Chat) -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "chat")

    mdb.insert_one(chat.to_insert())

def update_back_id (chat_id: ObjectId, back_id: ObjectId) -> bool:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "chat")
    if not isinstance(chat_id, ObjectId):
        chat_id = ObjectId(chat_id)

    mdb.update_one(
        filter={ "_id": chat_id },
        update_data={ "$set": { "back_id": ObjectId(back_id) }}
    )

def init_chat_db () -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "chat")

    mdb.drop_collection()
    mdb.create_index_keys(("_id"), (True, ))
