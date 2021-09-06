import base64
import json
import random
from datetime import datetime, timezone, timedelta
from io import BytesIO

import rsa
import yaml
from Crypto.Cipher import AES
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ocr.v20181119 import ocr_client, models


class Utils:
    def __init__(self):
        pass

    # 利用hook判断当前返回的状态码是否正常
    @staticmethod
    def checkStatus(request, *args, **kwargs):
        if request.status_code == 418:
            raise Exception('当前地区已被禁用，请使用其他地区的节点')

    # 获取当前北京时间
    @staticmethod
    def getAsiaTime():
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        asia_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
        return asia_dt.strftime('%H:%M:%S')

    # 获取当前北京日期
    @staticmethod
    def getAsiaDate():
        utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        asia_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
        return asia_dt.strftime('%Y-%m-%d')

    # 获取指定长度的随机字符
    @staticmethod
    def randString(length):
        baseString = "ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678"
        data = ''
        for i in range(length):
            data += baseString[random.randint(0, len(baseString) - 1)]
        return data

    @staticmethod
    def getYmlConfig(yaml_file='./login/system.yml'):
        file = open(yaml_file, 'r', encoding="utf-8")
        file_data = file.read()
        file.close()
        config = yaml.load(file_data, Loader=yaml.FullLoader)
        return dict(config)

    # RSA加密的实现
    @staticmethod
    def encryptRSA(message, m, e):
        mm = int(m, 16)
        ee = int(e, 16)
        rsa_pubkey = rsa.PublicKey(mm, ee)
        crypto = Utils._encrypt_rsa(message.encode(), rsa_pubkey)
        return crypto.hex()

    @staticmethod
    def _encrypt_rsa(message, pub_key):
        keylength = rsa.common.byte_size(pub_key.n)
        padded = Utils._pad_for_encryption_rsa(message, keylength)
        payload = rsa.transform.bytes2int(padded)
        encrypted = rsa.core.encrypt_int(payload, pub_key.e, pub_key.n)
        block = rsa.transform.int2bytes(encrypted, keylength)
        return block

    @staticmethod
    def _pad_for_encryption_rsa(message, target_length):
        message = message[::-1]
        max_msglength = target_length - 11
        msglength = len(message)
        padding = b''
        padding_length = target_length - msglength - 3
        for i in range(padding_length):
            padding += b'\x00'
        return b''.join([b'\x00\x00', padding, b'\x00', message])

    # aes加密的实现
    @staticmethod
    def encryptAES(password, key):
        randStrLen = 64
        randIvLen = 16
        ranStr = Utils.randString(randStrLen)
        ivStr = Utils.randString(randIvLen)
        aes = AES.new(bytes(key, encoding='utf-8'), AES.MODE_CBC, bytes(ivStr, encoding="utf8"))
        data = ranStr + password

        text_length = len(data)
        amount_to_pad = AES.block_size - (text_length % AES.block_size)
        if amount_to_pad == 0:
            amount_to_pad = AES.block_size
        pad = chr(amount_to_pad)
        data = data + pad * amount_to_pad

        text = aes.encrypt(bytes(data, encoding='utf-8'))
        text = base64.encodebytes(text)
        text = text.decode('utf-8').strip()
        return text

    # 通过url解析图片验证码
    @staticmethod
    def getCodeFromImg(res, imgUrl):
        response = res.get(imgUrl, verify=False)  # 将这个图片保存在内存
        # 得到这个图片的base64编码
        imgCode = str(base64.b64encode(BytesIO(response.content).read()), encoding='utf-8')
        # print(imgCode)
        try:
            cred = credential.Credential(Utils.getYmlConfig()['SecretId'], Utils.getYmlConfig()['SecretKey'])
            httpProfile = HttpProfile()
            httpProfile.endpoint = "ocr.tencentcloudapi.com"

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = ocr_client.OcrClient(cred, "ap-beijing", clientProfile)

            req = models.GeneralBasicOCRRequest()
            params = {
                "ImageBase64": imgCode
            }
            req.from_json_string(json.dumps(params))
            resp = client.GeneralBasicOCR(req)
            codeArray = json.loads(resp.to_json_string())['TextDetections']
            code = ''
            for item in codeArray:
                code += item['DetectedText'].replace(' ', '')
            if len(code) == 4:
                return code
            else:
                return Utils.getCodeFromImg(res, imgUrl)
        except TencentCloudSDKException as err:
            raise Exception('验证码识别出现问题了' + str(err.message))
