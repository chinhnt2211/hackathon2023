import json
from json import JSONEncoder
import datetime
from configs.env import ALLOWED_EXTENSIONS


class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()


def data_time_serialize(obj):
    return json.loads(json.dumps(obj, indent=4, cls=DateTimeEncoder))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
