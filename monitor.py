#!/usr/bin/python
# coding=utf-8


import requests
import json
import time
import os

nodename = "eosstore1111"
address = '54.168.92.89'

filepath1 = '/tmp/.status'
filepath2 = '/tmp/.n'
filepath3 = '/tmp/.m'
timeformat = '%Y-%m-%d %X'

print "当前监控的地址: %s" % (address)


def init_file():
    f1 = open(filepath1, 'w+')
    f1.write('0000')
    f1.close()
    f2 = open(filepath2, 'w+')
    f2.write('0')
    f2.close()
    f3 = open(filepath3, 'w+')
    f3.write('0')
    f3.close()


init_file()


class send_message(object):

    def __init__(self):
        pass

    def access_server(self):
        CorpID = "XXXXXXXX"
        Secret = "TXXXXXXXX"
        url1 = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (CorpID, Secret)
        r = requests.get(url1)
        # 获取access_token
        access_token = json.loads(r.text)['access_token']
        return access_token

    def send_weixin(self, nodename, messages, title):
        news = {
            # "touser": "wo_weixinni|d41d8cd98f00b204e9800998ecf8427e|Zhangshiqi|ChengSongsong",  # 用户ID    多个ID 可以用|隔开
            "touser": "wo_weixinni",
            "toparty": " 2 ",  # 部门ID
            "totag": "  ",
            "msgtype": "news",
            "agentid": 0,
            "news": {
                "articles": [
                    {
                        "title": "%s| %s" % (title, nodename),
                        "description": messages
                    },
                ]
            }
        }

        token = self.access_server()
        body = json.dumps(news, ensure_ascii=False)
        url4 = "https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=%s" % token
        r = requests.post(url4, data=body)
        status = json.loads(r.text)['errmsg']
        if status == 'ok':
            print "%s | 报警发送成功!" % nowtime
        else:
            print "%s | 报警发送失败!" % nowtime


class check_eos(object):

    def __init__(self):
        pass

    def get_info(self):
        url = "http://%s:8888/v1/chain/get_info" % address
        try:
            response = requests.request("GET", url, timeout=5)
            data = response.text
            head_block_num = json.loads(data)["head_block_num"]
            hbp = json.loads(data)["head_block_producer"]  # 这里简写为hbp
            # 判断分叉的俩个依据，主要是看lib值和hbp的值,如果lib的值出现持续不变的情况下，则有可能是分叉了；
            # 或者lib值持续变化，但hbp的字段在130秒后没有重复出现，则也有可能出现分叉，这里不用时间做计算，使用计数方式，21个节点，也就是说每22次上回重复出现，如果没有出现，则有可能出现分叉
            lib = str(json.loads(data)["last_irreversible_block_num"])

            laste_numb = int(self.set_file('read', filepath=filepath3))
            if self.diff_lib(lib):
                laste_numb = int(self.set_file('read', filepath=filepath3))
                laste_numb = self.diff_hbp(hbp, laste_numb)
            print u"%s | hbp: %s, lib: %s, head_block_num: %s, No.%s" % (nowtime, hbp, lib, head_block_num, laste_numb)

        except Exception, e:
            messages = "故障信息: EOS服务故障,接口异常\n故障时间: %s" % nowtime
            self.alarm(messages)
            info = "EOS服务故障:%s" % e
            print "%s | %s" % (nowtime, info)

    def diff_lib(self, lib):
        laste_numb = self.set_file('read', filepath=filepath1)
        n = int(self.set_file('read', filepath=filepath2))
        if laste_numb == lib:

            if n > 2:
                messages = "故障信息: 可能出现分叉,请注意!\n报警次数: 第%s次(若频繁报警，请尽快处理)\n故障时间: %s" % (n - 2, nowtime)
                info = '出现分叉'
                self.alarm(messages)
                n = str(n + 1)
                self.set_file('write', info=n, filepath=filepath2)
                print "%s | %s" % (nowtime, info)

            else:
                n = str(n + 1)
                print "%s | 可能出现分叉，第%s次预警" % (nowtime, n)
                self.set_file('write', info=n, filepath=filepath2)
            return False
        else:
            if n > 2:
                print "%s | 故障恢复" % nowtime
                messages = "%s 故障恢复\n恢复时间: %s" % (nodename, nowtime)
                self.alarm(messages, title='EOS故障恢复')

            self.set_file('write', info=lib, filepath=filepath1)
            self.set_file('write', info="0", filepath=filepath2)
            return True

    def diff_hbp(self, hbp, laste_numb):
        if hbp == nodename:
            if laste_numb > 21:
                messages = "恢复信息: 恢复出块，轮次第%s次\n报警时间: %s" % (laste_numb, nowtime)
                self.alarm(messages, title='EOS故障恢复')
            self.set_file('write', info="0", filepath=filepath3)

        else:
            laste_numb = int(laste_numb + 1)
            if laste_numb > 21:
                messages = "故障信息: 出现一轮未出块，轮次第%s次\n报警时间: %s" % (laste_numb, nowtime)
                print "%s | 出现一轮未出块，轮次第%s次" % (nowtime, laste_numb)
                self.alarm(messages)
            self.set_file('write', info=str(laste_numb), filepath=filepath3)
        return laste_numb

    def set_file(self, action, info=None, filepath=None):
        if action == 'write':
            f = open(filepath, 'w+')
            f.write(info)
            f.close()
        elif action == 'read':
            f = open(filepath, 'r')
            fp = f.readline()
            f.close()
            return fp

    def alarm(self, messages, title='EOS故障报警'):
        send = send_message()
        send.send_weixin(nodename, messages, title)


if __name__ == '__main__':
    while True:
        nowtime = time.strftime(timeformat, time.localtime())
        run = check_eos()
        run.get_info()
        time.sleep(6)
