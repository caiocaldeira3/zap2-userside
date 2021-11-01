import json
import flask
from sqlalchemy.ext.declarative import DeclarativeMeta

forbidden_fields = [
    "access",
    "date_created",
    "metadata",
    "password",
    "query",
    "query_class",
    "registry",
]

class AlchemyEncoder(json.JSONEncoder):

    def default(self: object, obj: object) -> any:
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [
                x for x in dir(obj)
                if not x.startswith('_') and x not in forbidden_fields
            ]:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)