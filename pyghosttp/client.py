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


class Expectation(object):
    def __init__(self, failed=False, reason=None):
        self.failed = failed
        self.reason = reason

    def is_pass(self):
        return not self.failed

    def is_failed(self):
        return self.failed

    def get_reason(self):
        return self.reason


class TestableBody(object):
    def __init__(self, data):
        self.data = data

    def contains(self, content):
        """
        Checks if the body has the requested content. Returns expectation with pass true otherwise false
        :param content: a string, dict or list that is expected in the content.
        :return: A expectation
        """
        if not isinstance(content, type(self.data)):
            return Expectation(True, "Invalid types. Expected: " +
                               str(content.__class__.__name__) + " got: " + str(self.data.__class__.__name__))
        elif isinstance(content, str) and isinstance(self.data, str):
            string_contained = content in self.data
            return Expectation(string_contained, "String not found in body " + str(self.data) if string_contained else None)
        elif isinstance(content, list) and isinstance(self.data, list):
            missing_items = list(set(content) - set(self.data))
            has_failed = len(missing_items) != 0
            return Expectation(has_failed, "Elements not found: " + str(missing_items))
        elif isinstance(content, dict) and isinstance(self.data, dict):
            missing_keys = []
            distinct_values = []
            data_transformed = {k.lower(): self.data[k].lower() for k in self.data}

            for key in content:
                key = key.lower()
                if key not in data_transformed:
                    missing_keys.append(key)
                elif content[key].lower() != data_transformed[key] and content[key].lower() not in data_transformed[key]:
                    distinct_values.append(key)

            is_missing_keys = len(missing_keys) != 0
            has_distinct_values = len(distinct_values) != 0
            has_failed = is_missing_keys or has_distinct_values

            reasons = []

            if has_failed:
                if is_missing_keys:
                    reasons.append("Missing keys: " + str(missing_keys))
                if has_distinct_values:
                    reasons.append("Distinct values: " + str(distinct_values))

            return Expectation(has_failed, reasons)

        raise Exception("Unsupported type")


class TestableClientResponse(ClientResponse):
    __SUPPORTED_TYPES = {
        'integer': int,
        'float': float,
        'string': str,
        'object': dict,
        'array': list
    }

    def body(self):
        return TestableBody(self.data)

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
