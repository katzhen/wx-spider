# 导入Flask类
from flask import request
from spider import app, spider
import json

# route()方法用于设定路由；类似于spring路由配置
@app.route('/', methods=['POST'])
def index():
    url = ""
    if request.json.__contains__("url"):
        url = request.json["url"]
    else:
        return '参数不能为空'
    page = 0
    if request.json.__contains__("page"):
        page = int(request.json["page"])
    params = spider.getParams(url, page)
    if isinstance(params, str):
        return params
    else:
        result = spider.readList(params)
        return result


@app.route('/details', methods=['POST'])
def details():
    result = spider.details()
    return result


if __name__ == '__main__':
    # app.run(host,port,debug,options)
    # 默认值：host="127.0.0.1",port=5000,debug=False
    app.run(host="localhost", port=5000)
