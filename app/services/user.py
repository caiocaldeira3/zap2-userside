from bson import ObjectId

from app.models.user import User
from app.util import config, mongodb


def find_with_telephone (tel: str) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    result = mdb.find_one({ "telephone": tel })
    if result is None:
        return None

    return User(**result)

def find_with_id (user_id: str) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    result = mdb.find_one({ "_id": user_id })
    if result is None:
        return None

    return User(**result)

def find_many (tels: list[str]) -> User:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return [
        User(**result)
        for result in mdb.find_many({ "telephone": {"$in": tels} })
    ]

def find_connected_users () -> list[User]:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return [
        User(**result)
        for result in mdb.find_many({ "socket_id": {"$ne": None} })
    ]

def insert_user (user: User) -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    print(user.to_insert())
    r = mdb.insert_one(user.to_insert())

    print(r)

def delete_user (tel: str) -> bool:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.find_one_and_delete({ "telephone": tel })

def disconect_users () -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.update_one(
        filter={ "socket_id": {"$ne": None} },
        update_data={ "$set": { "socket_id": None }}
    )

def update_user_name (user_id: str, name: str) -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    return mdb.update_one(
        filter={ "_id": ObjectId(user_id) },
        update_data={ "$set": { "name": name }}
    )

def add_user_device (user_id: str, socket_id: str) -> bool:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")
    if not isinstance(user_id, ObjectId):
        user_id = ObjectId(user_id)

    return mdb.update_one(
        filter={ "_id": user_id },
        update_data={ "$set": { "socket_id": socket_id }}
    )

def list_user () -> list[User]:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    print([
        User(**result)
        for result in mdb.find_many({})
    ])

def init_user_db () -> None:
    mdb = mongodb.Mongo(config.MONGO_CONN, config.MONGO_DB, "user")

    mdb.drop_collection()
    mdb.create_index_keys(("telephone"), (True, ))
