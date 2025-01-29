import os
import requests
import json
from flask import Flask, request, jsonify
from database import is_token_valid
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

IMEI_CHECK_API_KEY = os.getenv('IMEI_CHECK_API_KEY')
IMEI_CHECK_URL = 'https://api.imeicheck.net/v1/checks'

def is_valid_imei(imei: str) -> bool:
    return len(imei) == 15 and imei.isdigit()

def verify_token(token: str):
    if not is_token_valid(token):
        return False
    return True

def get_imei_info(imei: str):
    headers = {
        'Authorization': 'Bearer ' + IMEI_CHECK_API_KEY,
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        "deviceId": f"{imei}",
        "serviceId": 12 # для проверки Токен API Live использовать другой serviceId, например 20 или 21
    })
    response = requests.post(IMEI_CHECK_URL, headers=headers, data=data)
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"Ошибка при запросе к внешнему API: {response.status_code}")

@app.route('/api/check-imei', methods=['POST'])
def check_imei():
    data = request.json
    imei = data.get('imei')
    token = data.get('token')

    if not imei or not token:
        return jsonify({"status": "error", "message": "IMEI и токен обязательны"}), 400

    if not verify_token(token):
        return jsonify({"status": "error", "message": "Неверный токен"}), 403

    if not is_valid_imei(imei):
        return jsonify({"status": "error", "message": "Неверный IMEI"}), 400

    try:
        imei_info = get_imei_info(imei)
        return jsonify({"status": "success", "data": imei_info})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)