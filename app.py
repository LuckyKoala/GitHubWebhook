# coding=utf-8
# @Author: LuckyKoala
# @Time: 2020/11/5
# @File: app.py


from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/webhook/github', methods=['POST'])
def event_handler():
    json = request.get_json()
    print(str(json))
    return jsonify({
        "status": "ok"
    })
