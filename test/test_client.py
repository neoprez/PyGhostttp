from pyghosttp.client import TestableClient

if __name__ == '__main__':

    HEADERS = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    c = TestableClient('http://127.0.0.1:5000', headers=HEADERS)

    response = c.get('/hello-json')

    body = response.body()
    expect = body.contains({"hello": "world"})

    print response.is_2xx_response()
    print expect.is_pass(), expect.get_reason()
