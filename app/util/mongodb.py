from collections.abc import Iterable, Sequence
from typing import Any

import pymongo
from pymongo.client_session import ClientSession
from pymongo.errors import ConnectionFailure


def get_client (conn_str: str) -> pymongo.MongoClient:
    """
        Creates a client connection with the MongoDB and tests its connection
        permissions. Returns the client if made through mongomock
        :returns:    MongoClient.
    """
    client = pymongo.MongoClient(conn_str)
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command("ismaster")

        return client

    except ConnectionFailure as e:
        raise e

    except NotImplementedError:
        # Mongomock Client

        return client

class Mongo:
    """
        Class responsible for the connecton with the MongoDB and all
        CRUD related operations and queries.\n
        :database_name str:     the connected database\n
        :collection_name str:   the connected collection\n
        :client MongoClient:    the mongo client\n
        :db Database:           the connected mongo database\n
        :collection Collection: the connected mongo collection\n
    """
    database_name: str
    collection_name: str
    project_mongo_id: int

    def __init__ (
        self, conn_str: str, database: str, collection: str, project_mongo_id: bool = True
    ) -> None:
        """
            Initializes the Mongo connection to the informed database and collection, if
            the database is not provided the default will be the PYGATEWAY_DB.
        """
        self.database_name = database
        self.collection_name = collection

        self.client = get_client(conn_str)
        self.db = self.client[database]
        self.collection = self.db[collection]

        self.project_mongo_id = project_mongo_id

    def create_index_keys (
        self, index_keys: Iterable[str], unique: Sequence = ()
    )  -> None:
        for key in index_keys:
            is_unique = key in unique
            self.collection.create_index(key, unique=is_unique, name=key)

    def format_projection (self, projection: Iterable) -> dict[str, Any]:
        """
            Format the projection as a dictionary that can be processed by pymongo.
            :param projection:  the projection as a dictionary or list
            :returns:            the projection dictionary
        """
        if isinstance(projection, dict):
            return projection | { "_id": self.project_mongo_id }

        elif isinstance(projection, str):
            return {
                projection: 1,
                "_id": self.project_mongo_id
            }

        elif projection is None and self.project_mongo_id:
            return None

        elif projection is None:
            return { "_id": False }

        return { k: 1 for k in projection } | { "_id": self.project_mongo_id }

    def drop_collection (self) -> None:
        """
            Resets the collection information, should only be used for debug purposes.
        """
        self.db[self.collection_name].drop()
        self.collection = self.db[self.collection_name]

    def insert_one (self, data: dict[str, Any]) -> dict[str, Any]:
        """
            Inserts a formated dict[str, Any] to the connected collection.
            :param data:    the dict[str, Any]
            :returns:       a dictionary with the object id and its related user
        """
        result_id = self.collection.insert_one(data).inserted_id

        return result_id

    def update_one (
        self, filter: dict[str, Any], update_data: dict[str, dict[str, Any]]
    ) -> bool:
        """
            Updates a formated dict[str, Any] in the connected colletion, uses the filter data to
            find a match for the dict[str, Any], if no match is found the function adds the
            dict[str, Any] to the collection.
            :param filter:          the object identifiers filter
            :param data:            the objects new information
            :returns:               true if the query has been acknoledged and a object modified
        """
        result = self.collection.update_one(filter, update_data)

        return result.acknowledged and result.modified_count == 1

    def find_one (
        self, data: dict[str, Any], projection: Iterable = None, session: ClientSession = None
    ) -> dict[str, Any]:
        """
            Finds an Object that matches the query from the formatted dict[str, Any] and returns
            the values specified in the projection, if the projection is None it returns the
            whole object.
            :param data:        the dict[str, Any].
            :param projection:  iterable with keys relevant to the output.
            :param session:     parameter to write on transaction, should only be used
                                when connecting to a replica set
            :returns:                a dictionary with the key-values in projection
        """
        projection = self.format_projection(projection)

        return self.collection.find_one(data, projection=projection, session=session)

    def find_many (self, data: dict[str, Any]) -> pymongo.CursorType:
        return self.collection.find(data)

    def find_one_and_delete (self, data: dict[str, Any]) -> dict[str, Any]:
        """
            Find the matched object in the connected collection and deletes it
            :param data:    the dict[str, Any].
            :returns:       the projected deleted object or None if not found
        """

        return self.collection.find_one_and_delete(data)

    def aggregate_query (self, pipeline: list, session: ClientSession = None) -> dict[str, Any]:
        """
            Performs an agregate query thorugh the pipeline provided
            :param pipeline:    the query pipeline, a list of dictionaries
            :param session:     parameter to write on transaction, should only be used
                                when connecting to a replica set
            :returns:            the matched objects
        """
        result = self.collection.aggregate(pipeline, session=session)

        return result
