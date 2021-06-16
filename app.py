from flask import Flask, request, jsonify

from service.data_processing import voucher_selection_service, refresh_data_service

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'


@app.route('/refresh', methods=['POST'])
def refresh_data():
    req_body = request.json
    return jsonify(refresh_data_service(req_body))


@app.route('/select-voucher', methods=['POST'])
def voucher_selection():
    req_body = request.json
    return jsonify(voucher_selection_service(req_body))


if __name__ == '__main__':
    app.run(host='0.0.0.0')
