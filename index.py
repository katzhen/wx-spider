# 导入Flask类
from flask import request
from spider import app, spider
import uuid

# route()方法用于设定路由；类似于spring路由配置
@app.route('/', methods=['POST'])
def index():
    url = request.form["url"]
    params = spider.getParams(url)
    if isinstance(params, str):
        return params
    else:
        spider.readList(params)
        return '抓取成功'


if __name__ == '__main__':
    # app.run(host,port,debug,options)
    # 默认值：host="127.0.0.1",port=5000,debug=False
    app.run(host="localhost", port=5000)
