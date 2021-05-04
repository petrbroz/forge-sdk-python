import requests

class BaseClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    def _resolve_url(self, url):
        if url.startswith('/'):
            url = self.base_url + url
        return url

    def _get(self, url, params=None, headers=None):
        url = self._resolve_url(url)
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def _post(self, url, form=None, json=None, buff=None, params=None, headers=None):
        url = self._resolve_url(url)
        response = None
        if form:
            response = requests.post(url, data=form, params=params, headers=headers)
        elif form:
            response = requests.post(url, data=buff, params=params, headers=headers)
        elif json:
            response = requests.post(url, json=json, params=params, headers=headers)
        else:
            response = requests.post(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def _put(self, url, form=None, json=None, buff=None, params=None, headers=None):
        url = self._resolve_url(url)
        response = None
        if form:
            response = requests.put(url, data=form, params=params, headers=headers)
        elif buff:
            response = requests.put(url, data=buff, params=params, headers=headers)
        elif json:
            response = requests.put(url, json=json, params=params, headers=headers)
        else:
            response = requests.put(url, params=params, headers=headers)
        response.raise_for_status()
        return response
 
    def _delete(self, url, params=None, headers=None):
        url = self._resolve_url(url)
        response = requests.delete(url, params=params, headers=headers)
        response.raise_for_status()
        return response