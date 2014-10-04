import json, requests
from urllib import splitquery
from urlparse import urlparse as parse


class Collection(object):
    model = None

    def __init__(self, client):
        self.client = client

    def handle_error(self, response):
        import logging
        logger = logging.getLogger('dj_capysule')
        logger.error(response.text)
        response.raise_for_status()

    def decode(self, data, many=False):
        if many:
            result = []
            for d in data:
                obj = self.model(**self.model.decode(d))
                obj._persisted = True
                result.append(obj)
            return result
        else:
            return self.model(**self.model.decode(data))

    def encode(self, obj):
        return obj.encode()

    def all(self):
        response = self.client.fetch(self.url)

        if response.status_code >= 400:
            self.handle_error(response)

        data = response.json()

        return self.decode(response, data=data, many=True)

    def query(self, **kwargs):
        request = requests.Request('GET', self.url,
            params=kwargs,
            headers={'Content-Type': 'application/json'}
        )
        response = self.client.fetch(request)

        if response.status_code >= 400:
            self.handle_error(response)

        data = response.json()

        return self.decode(response, data=data, many=True)

    def get(self, id_):
        response = self.client.fetch(self._url(id_))

        if response.status_code >= 400:
            self.handle_error(response)

        data = response.json()

        return self.decode(response, data=data)

    def _url(self, id_):
        url = self.url

        if callable(url):
           return url(id_)

        url, query = splitquery(url)

        url = '{0}/{1}'.format(url, id_)

        if query is not None:
            url = '{0}?{1}'.format(url, query)

        return url

    def _parse_url(self, url):
        parse_url = getattr(self.model, '_parse_url', None)

        if callable(parse_url):
            return parse_url(url)

        parts = url.split('/')
        if len(parts):
            return parts[-1]
        else:
            return None

    def add(self, obj):
        if getattr(obj, '_persisted', False) is True:
            url = self._url(self._id(obj))
            method = 'PUT'
        else:
            url = getattr(obj, '_url', self.url)
            if callable(url):
                url = url()
            method = 'POST'

        data = self.encode(obj)

        request = requests.Request(method, url,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )

        response = self.client.fetch(request)

        if response.status_code >= 400:
            self.handle_error(response)

        if len(response.content) > 0:
            data = response.json()

            try:
                obj.decode(data)
                obj._persisted = True
            except Exception as error:
                raise

            return obj
        else:
            try:
                url = response.headers.get('Location')
            except KeyError:
                return None
            id_ = self._parse_url(url)
            if id_ is not None:
                for name, field in obj._fields.items():
                    if field.options.get('primary', False):
                        setattr(obj, name, id_)
                        return obj
            return None


    def _id(self, obj):
        for name, field in obj._fields.items():
            if field.options.get('primary', False):
                return getattr(obj, name)
