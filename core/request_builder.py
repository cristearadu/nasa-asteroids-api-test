import requests


def get_request(url, params=None):
    return requests.get(url, params=params)
