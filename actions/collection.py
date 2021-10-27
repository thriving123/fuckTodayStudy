import base64
import json
import os
import random
import re
import uuid
from pyDes import PAD_PKCS5, des, CBC
from requests_toolbelt import MultipartEncoder

from login.Utils import Utils
from todayLoginService import TodayLoginService
from liteTools import DT


class Collection:
    # 初始化信息收集类
    def __init__(self, todaLoginService: TodayLoginService, userInfo, encryptApi):
        self.session = todaLoginService.session
        self.host = todaLoginService.host
        self.userInfo = userInfo
        self.form = None
        self.collectWid = None
        self.formWid = None
        self.schoolTaskWid = None
        self.instanceWid = None
        self.encryptApi = encryptApi

    # 查询表单
    def queryForm(self):
        headers = self.session.headers
        headers['Content-Type'] = 'application/json'
        queryUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/queryCollectorProcessingList'
        params = {
            'pageSize': 20,
            "pageNumber": 1
        }
        res = self.session.post(queryUrl, data=json.dumps(
            params), headers=headers, verify=False)
        if res.status_code == 404:
            raise Exception('您没有任何信息收集任务，请检查自己的任务类型！')
        res = DT.resJsonEncode(res)
        if res['datas']['totalSize'] < 1:
            raise Exception('查询表单失败，当前没有信息收集任务哦！')
        self.collectWid = res['datas']['rows'][0]['wid']
        self.formWid = res['datas']['rows'][0]['formWid']
        self.instanceWid = res['datas']['rows'][0]['instanceWid']
        detailUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/detailCollector'
        res = self.session.post(detailUrl, headers=headers, data=json.dumps({'collectorWid': self.collectWid,'instanceWid': self.instanceWid}),
                                verify=False)
        res = DT.resJsonEncode(res)
        self.schoolTaskWid = res['datas']['collector']['schoolTaskWid']
        getFormUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/getFormFields'
        params = {"pageSize": 100, "pageNumber": 1,
                  "formWid": self.formWid, "collectorWid": self.collectWid, "instanceWid": self.instanceWid}
        res = self.session.post(
            getFormUrl, headers=headers, data=json.dumps(params), verify=False)
        res = DT.resJsonEncode(res)
        self.form = res['datas']['rows']

    # 上传图片到阿里云oss
    def uploadPicture(self, picSrc):
        url = f'{self.host}wec-counselor-collector-apps/stu/oss/getUploadPolicy'
        res = self.session.post(url=url, headers={'content-type': 'application/json'},
                                data=json.dumps({'fileType': 1}),
                                verify=False)
        datas = DT.resJsonEncode(res).get('datas')
        print(datas)
        fileName = datas.get('fileName')
        policy = datas.get('policy')
        accessKeyId = datas.get('accessid')
        signature = datas.get('signature')
        policyHost = datas.get('host')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0'
        }
        multipart_encoder = MultipartEncoder(
            fields={  # 这里根据需要进行参数格式设置
                'key': fileName + '.png', 'policy': policy, 'OSSAccessKeyId': accessKeyId,
                'success_action_status': '200',
                'signature': signature,
                'file': ('blob', open(picSrc, 'rb'), 'image/png')
            })
        headers['Content-Type'] = multipart_encoder.content_type
        self.session.post(url=policyHost,
                          headers=headers,
                          data=multipart_encoder)
        self.fileName = fileName

    # 获取图片上传位置
    def getPictureUrl(self):
        url = f'{self.host}wec-counselor-collector-apps/stu/collector/previewAttachment'
        params = {'ossKey': self.fileName}
        res = self.session.post(url=url, headers={'content-type': 'application/json'}, data=json.dumps(params),
                                verify=False)
        photoUrl = DT.resJsonEncode(res).get('datas') + '.png'
        print('图片地址：' + photoUrl)
        return photoUrl

    # 填写表单
    def fillForm(self):
        index = 0
        for formItem in self.form[:]:
            # 只处理必填项
            if formItem['isRequired']:
                userForm = self.userInfo['forms'][index]['form']
                # 判断是否忽略该题
                if 'ignore' in userForm and userForm['ignore']:
                    # 设置显示为false
                    formItem['show'] = False
                    # 清空所有的选项
                    if 'fieldItems' in formItem:
                        formItem['fieldItems'].clear()
                    index += 1
                    continue
                # 判断用户是否需要检查标题
                if self.userInfo['checkTitle'] == 1:
                    # 如果检查到标题不相等
                    if formItem['title'].strip() != userForm['title'].strip():
                        raise Exception(
                            f'\r\n第{index + 1}个配置项的标题不正确\r\n您的标题为："{userForm["title"]}"\r\n系统的标题为："{formItem["title"]}"')
                # 填充多出来的参数（新版增加了四个参数，暂时不知道作用）
                formItem['show'] = True
                formItem['formType'] = '0'  # 盲猜是任务类型、待确认
                formItem['sortNum'] = str(formItem['sort'])  # 盲猜是sort排序
                formItem['logicShowConfig'] = {}
                preSelect = []
                # 文本选项直接赋值
                if formItem['fieldType'] in ['1', '5', '6', '7']:
                    formItem['value'] = userForm['value']
                # 单选框填充
                elif formItem['fieldType'] == '2':
                    # 定义单选框的wid
                    itemWid = ''
                    # 单选需要移除多余的选项
                    fieldItems = formItem['fieldItems']
                    for fieldItem in fieldItems[:]:
                        if 'value' not in userForm:
                            raise Exception(
                                f"第{index + 1}个题目出错，题目标题为{formItem['sort']}{formItem['title']}")
                        if fieldItem['content'] != userForm['value']:
                            fieldItems.remove(fieldItem)
                            # 如果之前被选中
                            if fieldItem['isSelected']:
                                preSelect.append(fieldItem['content'])
                        else:
                            itemWid = fieldItem['itemWid']
                            # 当该字段需要填写且存在otherItemType类型时（其他字段）
                            if fieldItem['isOtherItems'] and fieldItem['otherItemType'] == '1':
                                # 当配置文件中不存在other字段时抛出异常
                                if 'other' not in userForm:
                                    raise Exception(
                                        f'\r\n第{index + 1}个配置项的选项不正确，该字段存在“other”字段，请在配置文件“title，value”下添加一行“other”字段并且填上对应的值'
                                    )
                                fieldItem['contentExtend'] = userForm['other']
                    if itemWid == '':
                        raise Exception(
                            f'\r\n第{index + 1}个配置项的选项不正确，该选项为单选，且未找到您配置的值\r\n您上次的选值为：{preSelect}'
                        )
                    formItem['value'] = itemWid
                # 多选填充
                elif formItem['fieldType'] == '3':
                    # 定义单选框的wid
                    itemWidArr = []
                    fieldItems = formItem['fieldItems']
                    userItems = userForm['value'].split('|')
                    for fieldItem in fieldItems[:]:
                        if fieldItem['content'] in userItems:
                            itemWidArr.append(fieldItem['itemWid'])
                            # 当该字段需要填写且存在otherItemType类型时（其他字段）
                            if fieldItem['isOtherItems'] and fieldItem['otherItemType'] == '1':
                                # 当配置文件中不存在other字段时抛出异常
                                if 'other' not in userForm:
                                    raise Exception(
                                        f'\r\n第{index + 1}个配置项的选项不正确，该字段存在“other”字段，请在配置文件“title，value”下添加一行“other”字段并且填上对应的值'
                                    )
                                fieldItem['contentExtend'] = userForm['other']
                        else:
                            fieldItems.remove(fieldItem)
                            if fieldItem['isSelected']:
                                preSelect.append(fieldItem['content'])
                    # 若多选一个都未选中
                    if len(itemWidArr) == 0:
                        raise Exception(
                            f'\r\n第{index + 1}个配置项的选项不正确，该选项为多选，且未找到您配置的值\r\n您上次的选值为：{preSelect}'
                        )
                    formItem['value'] = ','.join(itemWidArr)
                # 图片（健康码）上传类型
                elif formItem['fieldType'] == '4':
                    # 如果是传图片的话，那么是将图片的地址（相对/绝对都行）存放于此value中
                    picBase = userForm['value']
                    # 如果直接是图片
                    if os.path.isfile(picBase):
                        picSrc = picBase
                    else:
                        picDir = os.listdir(picBase)
                        # 如果该文件夹里没有文件
                        if len(picDir) == 0:
                            raise Exception("您的图片上传已选择一个文件夹，且文件夹中没有文件！")
                        # 拼接随机图片的图片路径
                        picSrc = os.path.join(picBase, random.choice(picDir))
                    self.uploadPicture(picSrc)
                    formItem['value'] = self.getPictureUrl()
                    # 填充其他信息
                    formItem.setdefault('http', {
                        'defaultOptions': {
                            'customConfig': {
                                'pageNumberKey': 'pageNumber',
                                'pageSizeKey': 'pageSize',
                                'pageDataKey': 'pageData',
                                'pageTotalKey': 'pageTotal',
                                'data': 'datas',
                                'codeKey': 'code',
                                'messageKey': 'message'
                            }
                        }
                    })
                    formItem['uploadPolicyUrl'] = '/wec-counselor-collector-apps/stu/oss/getUploadPolicy'
                    formItem['saveAttachmentUrl'] = '/wec-counselor-collector-apps/stu/collector/saveAttachment'
                    formItem['previewAttachmentUrl'] = '/wec-counselor-collector-apps/stu/collector/previewAttachment'
                    formItem['downloadMediaUrl'] = '/wec-counselor-collector-apps/stu/collector/downloadMedia'
                else:
                    raise Exception(
                        f'\r\n第{index + 1}个配置项属于未知配置项，请反馈'
                    )
                index += 1
            else:
                # 移除非必填选项
                self.form.remove(formItem)

    # 提交表单
    def submitForm(self):
        deviceId = str(uuid.uuid1())
        model = "RuoLi Phone Plus Pro Max 2021"
        appVersion = "9.0.12"
        extension = {
            "model": model,
            "appVersion": appVersion,
            "systemVersion": "11",
            "userId": self.userInfo['username'],
            "systemName": "android",
            "lon": self.userInfo['lon'],
            "lat": self.userInfo['lat'],
            "deviceId": deviceId
        }

        headers = {
            'User-Agent': self.session.headers['User-Agent'],
            'CpdailyStandAlone': '0',
            'extension': '1',
            'Cpdaily-Extension': self.DESEncrypt(json.dumps(extension)),
            'Content-Type': 'application/json; charset=utf-8',
            # 请注意这个应该和配置文件中的host保持一致
            'Host': re.findall('//(.*?)/', self.host)[0],
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        }

        forBody = {
            "formWid": self.formWid, "address": self.userInfo['address'], "collectWid": self.collectWid,
            "instanceWid": self.instanceWid,
            "schoolTaskWid": self.schoolTaskWid, "form": self.form, "uaIsCpadaily": True,
            "latitude": self.userInfo['lat'], 'longitude': self.userInfo['lon']
        }

        forSubmit = {
            "appVersion": appVersion,
            "deviceId": deviceId,
            "lat": self.userInfo['lat'],
            "lon": self.userInfo['lon'],
            "model": model,
            "systemName": "android",
            "systemVersion": "11",
            "userId": self.userInfo['username'],
        }
        forBody = json.dumps(forBody, ensure_ascii=False)
        print(f'{Utils.getAsiaTime()} 正在请求加密数据...')
        res = self.session.post(self.encryptApi, params=forSubmit, data=forBody.encode("utf-8"), verify=False)
        if res.status_code != 200:
            raise Exception("加密表单数据出错，请反馈")
        res = res.json()
        if res['status'] != 200:
            raise Exception(res['message'])
        forSubmit['version'] = 'first_v2'
        forSubmit['calVersion'] = 'firstv'
        forSubmit['bodyString'] = res['data']['bodyString']
        forSubmit['sign'] = res['data']['sign']
        submitUrl = f'{self.host}wec-counselor-collector-apps/stu/collector/submitForm'
        res = self.session.post(
            submitUrl, headers=headers, data=json.dumps(forSubmit), verify=False)
        res = DT.resJsonEncode(res)
        return res['message']

    # DES加密
    def DESEncrypt(self, content):
        key = 'b3L26XNL'
        iv = b"\x01\x02\x03\x04\x05\x06\x07\x08"
        k = des(key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        encrypt_str = k.encrypt(content)
        return base64.b64encode(encrypt_str).decode()
