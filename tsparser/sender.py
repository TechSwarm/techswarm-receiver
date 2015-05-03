import urllib.request
import urllib.parse
from tsparser.auth import generate_auth
from tsparser import config


def send_data(data, url):
    """
    Send data to server

    :param data: data to send
    :type data: dict
    :param url: url where data are sent to
    :type url: str
    :return True if data have been sent successfully; False otherwise
    :rtype bool
    """
    header = {
        'Authorization': generate_auth(config.USERNAME, config.PASSWORD)
        }

    payload = urllib.parse.urlencode(data).encode('utf-8')
    request = urllib.request.Request(url, payload, header)
    try:
        response = urllib.request.urlopen(request)
    except urllib.request.HTTPError:
        return False
    return response == 201
