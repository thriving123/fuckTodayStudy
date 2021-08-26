import requests
import time
from login.Utils import Utils

# 获取当前日期，格式为 2021-8-22
def getNowDate():
    return time.strftime("%Y-%m-%d", time.localtime(time.time()))


# 获取当前时间，格式为 12:00:00
def getNowTime():
    return time.strftime("%H:%M:%S", time.localtime(time.time()))


# 若离消息通知类
class RlMessage:
    # 初始化类
    def __init__(self, sendKey, apiUrl, msgKey, sendType):
        self.sendKey = sendKey
        self.apiUrl = apiUrl
        self.msgKey = msgKey
        self.sendType = sendType

    # 发送邮件消息
    def sendMail(self, status, msg):
        # 若离邮件api， 将会存储消息到数据库，并保存1周以供查看，请勿乱用，谢谢合作
        if self.sendKey == '':
            return '邮箱为空，已取消发送邮件！'
        if self.apiUrl == '':
            return '邮件API为空，设置邮件API后才能发送邮件'
        params = {
            'reciever': self.sendKey,
            'title': f'[{status}]今日校园通知',
            'content': f'[{Utils.getAsiaDate()} {Utils.getAsiaTime()}]{msg}'
        }
        res = requests.post(url=self.apiUrl, params=params).json()
        return res['message']

    # qmsg推送
    def sendQmsg(self, status, msg):
        if self.sendKey == '':
            return 'QQ为空，已取消发送邮件！'
        if self.msgKey == '':
            return 'QmsgKey为空，设置QmsgKey后才能发送QQ推送'
        params = {
            'msg': f'[{Utils.getAsiaDate()} {Utils.getAsiaTime()}]{msg}',
            'qq': self.sendKey
        }
        res = requests.post(f'https://qmsg.zendee.cn/send/{self.msgKey}', params).json()
        return res['reason']

    # 其他通知方式待添加

    # 统一发送接口名
    def send(self, status, msg):
        print(Utils.getAsiaTime()+' 正在发送邮件通知')
        if self.sendType == 0:
            return self.sendMail(status, msg)
        elif self.sendType == 1:
            time.sleep(2)
            return self.sendQmsg(status, msg)
        elif self.sendType == 2:
            # 更多推送方式待添加
            return
