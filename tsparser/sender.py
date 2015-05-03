import requests
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
    try:
        response = requests.post(url, data=data,
                                 auth=(config.USERNAME, config.PASSWORD))
    except requests.HTTPError:
        return False
    return response.status_code == 201
