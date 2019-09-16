import urllib2
import urllib
import json


# Http Headers http://jkorpela.fi/http.html
class ClientResponse(object):
    def __init__(self, url, info, data, code):
        self.url = url
        self.info = info
        self.data = data
        self.code = code

    def __str__(self):
        return str(self.data)

    def __repr__(self):
        return self.__str__()


class Client(object):
    def __init__(self, base_url, headers=None):
        self.base_url = base_url
        self.headers = {} if not headers else headers.copy()

    def __open(self, path, data):
        request = urllib2.Request(self.base_url + path, data=data, headers=self.headers)
        return urllib2.urlopen(request)

    def __handle_request(self, path, data):
        try:
            response = self.__open(path, data)
            info = response.info()
            if 'application/json' in info['Content-Type']:
                response_data = json.loads(response.read())
            else:
                response_data = response.read()
            return ClientResponse(response.geturl(), info, response_data, response.getcode())
        except urllib2.HTTPError as http_error:
            return ClientResponse(self.base_url + path, http_error.info(), http_error.read(), http_error.code)

    def post(self, path, data):
        if self.headers and 'application/json' in self.headers['Content-Type']:
            data = json.dumps(data)
        else:
            data = urllib.urlencode(data)
        return self.__handle_request(path, data)

    def get(self, path, data=None):
        if data:
            path = path + "?" + urllib.urlencode(data)
        return self.__handle_request(path, data)


class TestableClientResponse(ClientResponse):
    def is_2xx_response(self):
        return 200 <= self.code < 300

    def is_3xx_response(self):
        return 300 <= self.code < 400

    def is_4xx_response(self):
        return 400 <= self.code < 500


class TestableClient(Client):
    @staticmethod
    def __to_testable_client_response(response):
        return TestableClientResponse(response.url, response.info, response.data, response.code)

    def get(self, path, data=None):
        return TestableClient.__to_testable_client_response(super(TestableClient, self).get(path, data=data))

    def post(self, path, data=None):
        return TestableClient.__to_testable_client_response(super(TestableClient, self).post(path, data=data))
