# coding=utf-8
# @Author: LuckyKoala
# @Time: 2020/11/5
# @File: app.py
import configparser
import hmac
import subprocess
from pathlib import Path
from threading import Thread

from flask import Flask, request, jsonify, abort

app = Flask(__name__)

config_path_str = os.path.join(os.path.abspath(os.curdir), "config.ini")
config_path = Path(config_path_str)
if not config_path.is_file():
    app.logger.warning("config.ini not found, try copy config-default.ini to config.ini and do according editing")
config_parser = configparser.ConfigParser()
config_parser.read(config_path_str, encoding="utf8")

mappings = config_parser["Mappings"]

TOKEN = os.environ.get("GITHUB_WEBHOOK_SECRET_TOKEN", "FooBar")
app.logger.debug("Token is " + TOKEN)

@app.route('/webhook/github', methods=['POST'])
def event_handler():
    # 判断事件类型和签名
    github_event = request.headers.get("X-GitHub-Event")
    github_signature_sha256 = request.headers.get("X-Hub-Signature-256")

    if github_event is None:
        app.logger.debug("github_event is None")
        abort(400)
    elif github_event == "ping":
        return jsonify({
            "status": "ok"
        })
    elif github_event != "push" or github_signature_sha256 is None:
        app.logger.debug("event not push or signature is None")
        abort(400)

    # 验证签名
    signature = hmac.new(
        key=str.encode(TOKEN),
        msg=request.data,
        digestmod="sha256").hexdigest()

    if not hmac.compare_digest(github_signature_sha256, "sha256="+signature):
        app.logger.debug(f"{github_signature_sha256} not equal to {signature}")
        abort(400)

    # 判断更新的仓库、分支和推送者
    json = request.get_json()
    try:
        ref = json["ref"]
        repo_name = json["repository"]["name"]
        commit_id_after = json["after"]
        sender_login = json["sender"]["login"]
    except KeyError as e:
        app.logger.debug("KeyError => " + str(e))
        abort(400)

    app.logger.info(f"<{commit_id_after}> {sender_login} push to {repo_name} with {ref}")

    branch = ref.split("refs/heads/")[1]
    key = f"{repo_name}/{branch}"
    if key in mappings:
        cmd = mappings[key]
        Thread(target=exec_shell_script, args=(cmd,), daemon=True).start()

    return jsonify({
        "status": "ok"
    })


def exec_shell_script(script):
    app.logger.info(f"executing shell script from {script}")
    subprocess.run(args=script.split(" "))
