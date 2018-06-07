#!/usr/bin/python
# coding=utf-8


import requests
import json
import time

Produced = "eosphereiobp"
address = '13.211.220.84'

timeformat = '%Y-%m-%d %X'

print "当前监控的地址: %s" % (address)

id_list = {'lib': 0, 'libn': 0, 'numberDisplay': 0}


class send_message(object):

    def __init__(self):
        pass

    def access_server(self):
        CorpID = "wx737b306e7efcf40c"
        Secret = "T3CLEw4s--q4624WxF3BT_wgdzgidZXXNcoJkpfqJi1dTlvZQWi9JtPDi1-hr3ND"
        url1 = "https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" % (CorpID, Secret)
        r = requests.get(url1)
        # 获取access_token
        access_token = json.loads(r.text)['access_token']
        return access_token

    def send_weixin(self, Produced, messages, title):
        news = {
            "touser": "wo_weixinni|d41d8cd98f00b204e9800998ecf8427e|Zhangshiqi|ChengSongsong",  # 用户ID    多个ID 可以用|隔开
            # "touser": "wo_weixinni",
            "toparty": " 2 ",  # 部门ID
            "totag": "  ",
            "msgtype": "news",
            "agentid": 0,
            "news": {
                "articles": [
                    {
                        "title": "%s| %s" % (title, Produced),
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
            lib = json.loads(data)["last_irreversible_block_num"]
            if self.diff_lib(lib):
                numberDisplay = self.diff_hbp(hbp)
            else:
                numberDisplay = id_list['numberDisplay']
            print "%s | hbp: %s, lib: %s, head_block_num: %s, No.%s" % (
                nowtime, hbp, lib, head_block_num, numberDisplay)
            print id_list

        except Exception, e:
            messages = "故障信息: EOS服务故障,接口异常\n故障时间: %s" % nowtime
            self.alarm(messages)
            info = "EOS服务故障:%s" % e
            print "%s | %s" % (nowtime, info)

    def diff_lib(self, lib):
        laste_numb = id_list['lib']
        libn = id_list['libn']
        if laste_numb == lib:

            if libn > 2:
                messages = "故障信息: 可能出现分叉,请注意!\n报警次数: 第%s次(若频繁报警，请尽快处理)\n故障时间: %s" % (libn - 2, nowtime)
                info = '出现分叉'
                self.alarm(messages)
                libn = libn + 1
                print "%s | %s" % (nowtime, info)

            else:
                libn = libn + 1
                print "%s | 可能出现分叉，第%s次预警" % (nowtime, libn)
            id_list['libn'] = libn
            return False
        else:
            if libn > 3:
                print "%s | 故障恢复" % nowtime
                messages = "%s 故障恢复\n恢复时间: %s" % (Produced, nowtime)
                self.alarm(messages, title='EOS故障恢复')

            id_list['lib'] = lib
            id_list['libn'] = 0
            return True

    def diff_hbp(self, hbp):
        numberDisplay = id_list['numberDisplay']
        if hbp == Produced:
            if numberDisplay > 21:
                messages = "恢复信息: 恢复出块，轮次第%s次\n报警时间: %s" % (numberDisplay, nowtime)
                self.alarm(messages, title='EOS故障恢复')
            id_list['numberDisplay'] = 1
            return 1

        else:
            numberDisplay = numberDisplay + 1
            if numberDisplay > 21:
                numb = numberDisplay / 21
                messages = "故障信息: 出现%s轮未出块，轮次第%s次\n报警时间: %s" % (numb, numberDisplay, nowtime)
                print "%s | 出现%s轮未出块，轮次第%s次" % (nowtime, numb, numberDisplay)
                print "请尽快切换备节点"
                self.alarm(messages)
                id_list['numberDisplay'] = numberDisplay
            else:
                id_list['numberDisplay'] = numberDisplay
            return numberDisplay

    def alarm(self, messages, title='EOS故障报警'):
        send = send_message()
        send.send_weixin(Produced, messages, title)


if __name__ == '__main__':
    while True:
        nowtime = time.strftime(timeformat, time.localtime())
        run = check_eos()
        run.get_info()
        time.sleep(6)
