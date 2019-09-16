from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route('/')
def hello_word():
    return 'Hello, world!'


@app.route('/hello-json')
def hello_json():
    return {"Hello": "world"}


@app.route('/hello-post', methods=['POST'])
def hello_post():
    return jsonify({ "name": request.json['name'] })


if __name__ == '__main__':
    app.run(debug=True)
