import urllib.request
import urllib.parse
from tsparser.auth import generate_auth
from tsparser import config


def send_data(data, url):
    """
    Send data to server

    :param data: data to send
    :type data: dictionary
    :param url: url where data are sent to
    :type url: str
    :return True if data have been sent successfully; False otherwise
    :rtype bool
    """
    header = {'Authorization': generate_auth(config.USERNAME, config.PASSWORD)}

    payload = urllib.parse.urlencode(data).encode('utf-8')
    print(payload)
    request = urllib.request.Request(url, payload, header)
    response = urllib.request.urlopen(request)
    if response.status == 201:
        return True
    return False