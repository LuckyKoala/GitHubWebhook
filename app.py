# coding=utf-8
# @Author: LuckyKoala
# @Time: 2020/11/5
# @File: app.py
import hmac
import os

from flask import Flask, request, jsonify, abort

app = Flask(__name__)


@app.route('/webhook/github', methods=['POST'])
def event_handler():
    # 判断事件类型和签名
    github_event = request.headers.get("X-GitHub-Event")
    github_signature_sha256 = request.headers.get("X-Hub-Signature-256")

    if github_event is None:
        abort(400)
    elif github_event == "ping":
        return jsonify({
            "status": "ok"
        })
    elif github_event != "push" or github_signature_sha256 is None:
        abort(400)

    # 验证签名
    signature = hmac.new(
        key=str.encode(os.environ.get("GITHUB_WEBHOOK_SECRET_TOKEN", "FooBar")),
        msg=request.data,
        digestmod="sha256").hexdigest()

    if not hmac.compare_digest(github_signature_sha256, "sha256="+signature):
        print(f"{github_signature_sha256} not equal to {signature}")
        abort(400)

    # 判断更新的仓库、分支和推送者
    json = request.get_json()
    try:
        ref = json["ref"]
        repo_full_name = json["repository"]["full_name"]
        commit_id_after = json["after"]
        sender_login = json["sender"]["login"]
    except KeyError:
        abort(400)

    print(f"<{commit_id_after}> {sender_login} push to {repo_full_name} with {ref}")

    return jsonify({
        "status": "ok"
    })
