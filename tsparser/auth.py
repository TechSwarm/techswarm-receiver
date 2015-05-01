import base64


def generate_auth(username, password):
    """
    Generate authorization header in Basic HTTP format
    :param username: username of client
    :type username: str
    :param password: password of client
    :type password: str
    :return: encoded authorization message
    :rtype: str
    """
    return 'Basic ' + base64.b64encode((username + ":" + password).encode('utf-8')).decode('utf-8')