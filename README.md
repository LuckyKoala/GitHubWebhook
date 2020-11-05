## 主要功能

* 使用 Flask 搭建
* 支持 GitHub WebHook
* 支持 `ping` 和 `push` 两个事件
* 支持签名验证

## 用法说明

> 实际生产环境需搭配 WSGI 使用

```bash
# 安装依赖
pip install -r requirement.txt
FLASK_APP=app.py flask run 
```