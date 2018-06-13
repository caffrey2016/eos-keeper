# -*- coding: utf-8 -*-
# coding=utf-8
import requests

url = "https://dx.ipyy.net/smsJson.aspx"

message = "线上服务异常，请及时处理!@亚伟"
sign = '【运维部】'

querystring = {"action": "send",
               "userid": "52483",
               "account": "AA00869",
               "password": "XXXXXXXXXXXXXXXXX",
               "mobile": "18210506606,13521319337,18610881110,15321985269",
               "content": message + sign,
               "sendTime": "", "extno": ""}

headers = {
    'Cache-Control': "no-cache",
    'Postman-Token': "0bca5e96-cd0e-4768-8b44-112ec66336ea"
}

response = requests.request("GET", url, headers=headers, params=querystring)
print response.text
