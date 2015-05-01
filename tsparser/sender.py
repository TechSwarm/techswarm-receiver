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
    data['Authorization'] = generate_auth(config.USERNAME, config.PASSWORD)

    request = urllib.request.Request(url, headers=data)
    urllib.request.urlopen(request)
    # todo check response and return True or False