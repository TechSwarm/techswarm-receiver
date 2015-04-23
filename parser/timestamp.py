from datetime import datetime

DT_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def get_timestamp():
    """
    Serialize actual datetime provided as simplified ISO 8601 (without timezone)
    string

    :type datetime: datetime
    :param datetime: datetime object to convert to string
    :return: serialized datetime
    :rtype: str
    """
    return datetime.now().strftime(DT_FORMAT)
