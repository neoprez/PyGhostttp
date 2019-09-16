from pyghosttp.client import TestableClient

if __name__ == '__main__':

    HEADERS = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    c = TestableClient('http://127.0.0.1:5000', headers=HEADERS)

    response = c.post('/hello-post', data={'name': 'Rodny'})

    print response.is_2xx_response()
