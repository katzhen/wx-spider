#!/usr/bin/python
# -*- coding: UTF-8 -*-
import requests
import json
import time
import re
import datetime
import urllib3
import uuid
import os
from spider import db
from .models import Articles

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36"
}

# 获取列表的参数
params = {
    "action": "getmsg",
    "__biz": "",  # 需获取
    "offset": 0,
    "count": 10,
    "is_ok": 1,
    "scene": 124,  # 根据提供的url获取
    "uin": "",  # 需获取
    "key": "",  # 需获取
    "pass_ticket": "",  # 需获取
    "wxtoken": "",
    "appmsg_token": "",  # 需获取
    "x5": 0,
    "f": "json"
}

# 解析url和页面内容组装请求列表的参数


def getParams(url):
    req = requests.get(url, headers=headers, verify=False)
    req.encoding = "UTF-8"
    text = req.text
    biz_str = re.search('&__biz=([^&]*)', url)
    if biz_str:
        params["__biz"] = biz_str.group().replace(
            '&__biz=', '')
    else:
        return '__biz匹配失败'
    scene_str = re.search('&scene=([^&]*)', url)
    if scene_str:
        params["scene"] = int(scene_str.group().replace(
            '&scene=', ''))
    else:
        return 'scene匹配失败'
    uin_str = re.search('var uin = \"([^\"]*)', text)
    if uin_str:
        params["uin"] = uin_str.group().replace(
            'var uin = \"', '')
    else:
        return 'uin匹配失败'
    key_str = re.search('var key = \"([^\"]*)', text)
    if key_str:
        params["key"] = key_str.group().replace(
            'var key = \"', '')
    else:
        return 'key匹配失败'
    pass_ticket_str = re.search('var pass_ticket = \"([^\"]*)', text)
    if pass_ticket_str:
        params["pass_ticket"] = pass_ticket_str.group().replace(
            'var pass_ticket = \"', '')
    else:
        return 'pass_ticket匹配失败'
    appmsg_token_str = re.search('window.appmsg_token = \"([^\"]*)', text)
    if appmsg_token_str:
        params["appmsg_token"] = appmsg_token_str.group().replace(
            'window.appmsg_token = \"', '')
    else:
        return 'appmsg_token匹配失败'
    return params


def writeLog(msg):
    now = datetime.datetime.now()
    path = "{0}/logs/{1}".format(os.path.abspath(os.path.dirname(os.path.dirname(__file__))),
                                 now.strftime("%Y%m"))
    if not os.path.exists(path):
        os.makedirs(path)
    filename = "{0}/{1}.log".format(path, now.strftime("%d"))
    f = open(filename, 'a', encoding='utf-8')
    content = "[{0}]:{1}\r\n".format(now.strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(content)
    f.write(content)
    f.close()


def readList(params):
    # 增加重连次数
    requests.adapters.DEFAULT_RETRIES = 5
    session = requests.session()
    # 关闭多余连接
    session.keep_alive = False
    req = requests.get('https://mp.weixin.qq.com/mp/profile_ext',
                       headers=headers, params=params, verify=False)
    req.encoding = "UTF-8"
    result = json.loads(req.text)
    list = []
    if result["ret"] == 0:
        if result["can_msg_continue"] == 1:
            # 读取下一页
            params["offset"] = result["next_offset"]
        else:
            params["offset"] = -1
        general_msg_list = json.loads(result["general_msg_list"])
        for item in general_msg_list["list"]:
            comm_msg_info = item['comm_msg_info']
            if item.__contains__('app_msg_ext_info') == False:
                continue
            ext_info = item['app_msg_ext_info']
            id = comm_msg_info["id"]
            dt_str = comm_msg_info["datetime"]
            dt = datetime.datetime.fromtimestamp(int(dt_str))
            con_dict = {}
            con_dict["id"] = id
            con_dict["datetime"] = dt
            con_dict["title"] = ext_info["title"]
            con_dict["url"] = ext_info["content_url"]
            con_dict["cover"] = ext_info["cover"]
            list.append(con_dict)
            if ext_info["is_multi"] == 1:
                for multi_item in ext_info["multi_app_msg_item_list"]:
                    item_dict = {}
                    item_dict["id"] = id
                    item_dict["datetime"] = dt
                    item_dict["title"] = multi_item["title"]
                    item_dict["url"] = multi_item["content_url"]
                    item_dict["cover"] = multi_item["cover"]
                    list.append(item_dict)

        for item in list:
            article = Articles(
                id=str(uuid.uuid4()),
                original_id=item["id"],
                title=item["title"],
                url=item["url"],
                cover=item["cover"],
                content='',
                publish_time=item["datetime"].strftime("%Y-%m-%d %H:%M:%S"),
                create_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            # print(article)
            db.session.add(article)
        db.session.commit()
        if params["offset"] != -1:
            writeLog('第{0}页读取完成，10s后读取下一页'.format(int(params["offset"]/10)))
            time.sleep(10)
            readList(params)
        else:
            writeLog('读取完成')
    else:
        print('地址失效')
