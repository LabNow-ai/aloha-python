import json
from datetime import datetime

from pandas._libs.tslibs.nattype import NaTType
from pandas._libs.tslibs.timestamps import Timestamp


class ObjectWithDateTimeEncoder(json.JSONEncoder):
    """
    JSON encoder that handles datetime and pandas timestamp objects.

    Converts:
    - pandas NaT to None
    - pandas Timestamp to Unix timestamp (float)
    - datetime objects to Unix timestamp (float)
    """

    def default(self, obj):
        """
        Convert objects to JSON serializable types.

        :param obj: Object to encode
        :return: JSON serializable representation
        """
        if isinstance(obj, NaTType):  # notice: NaTType is a subclass of datetime
            return None
        if isinstance(obj, Timestamp):
            return obj.timestamp()
        if isinstance(obj, datetime):
            return obj.timestamp()

        return json.JSONEncoder.default(self, obj)
