"""
Helper classes used by other API clients.
"""

import requests


class BaseClient:
    """
    Base client for accessing web-based APIs.
    """
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _resolve_url(self, url: str) -> str:
        if url.startswith("/"):
            url = self.base_url + url
        return url

    def _head(self, url: str, **kwargs) -> requests.Response:
        url = self._resolve_url(url)
        response = requests.head(url, **kwargs)
        response.raise_for_status()
        return response

    def _get(self, url: str, **kwargs) -> requests.Response:
        url = self._resolve_url(url)
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return response

    def _post(
        self, url: str, form: dict = None, json: dict = None, buff=None, **kwargs
    ) -> requests.Response:
        url = self._resolve_url(url)
        response = None
        if form:
            response = requests.post(url, data=form, **kwargs)
        elif form:
            response = requests.post(url, data=buff, **kwargs)
        elif json:
            response = requests.post(url, json=json, **kwargs)
        else:
            response = requests.post(url, **kwargs)
        response.raise_for_status()
        return response

    def _put(
        self, url: str, form: dict = None, json: dict = None, buff=None, **kwargs
    ) -> requests.Response:
        url = self._resolve_url(url)
        response = None
        if form:
            response = requests.put(url, data=form, **kwargs)
        elif buff:
            response = requests.put(url, data=buff, **kwargs)
        elif json:
            response = requests.put(url, json=json, **kwargs)
        else:
            response = requests.put(url, **kwargs)
        response.raise_for_status()
        return response

    def _delete(self, url: str, **kwargs) -> requests.Response:
        url = self._resolve_url(url)
        response = requests.delete(url, **kwargs)
        response.raise_for_status()
        return response
