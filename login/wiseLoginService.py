import re
import requests
from urllib3.exceptions import InsecureRequestWarning
from login.casLogin import casLogin
from login.iapLogin import iapLogin

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class wiseLoginService:
    # 初始化本地登录类
    def __init__(self, userInfo):
        if None == userInfo['username'] or '' == userInfo[
                'username'] or None == userInfo['password'] or '' == userInfo[
                    'password'] or None == userInfo[
                        'schoolName'] or '' == userInfo['schoolName']:
            raise Exception('初始化类失败，请键入完整的参数（用户名，密码，学校名称）')
        self.username = userInfo['username']
        self.password = userInfo['password']
        self.schoolName = userInfo['schoolName']
        self.session = requests.session()
        headers = {
            'User-Agent':
            'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',
        }
        self.session.headers = headers
        self.login_url = ''
        self.campus_host = ''
        self.login_host = ''
        self.loginEntity = None
        self.login_type = ''

    # 通过学校名称借助api获取学校的登陆url
    def getLoginUrlBySchoolName(self):
        schools = self.session.get(
            'https://mobile.campushoy.com/v6/config/guest/tenant/list',
            verify=False).json()['data']
        flag = False
        for item in schools:
            if item['name'] == self.schoolName:
                flag = True
                if item['joinType'] == 'NONE':
                    raise Exception(self.schoolName + '未加入今日校园，请检查...')
                params = {'ids': item['id']}
                data = self.session.get(
                    'https://mobile.campushoy.com/v6/config/guest/tenant/info',
                    params=params,
                    verify=False,
                ).json()['data'][0]
                joinType = data['joinType']
                ampUrl = data['ampUrl']
                ampUrl2 = data['ampUrl2']
                if 'campusphere' in ampUrl:
                    clientUrl = ampUrl
                elif 'campusphere' in ampUrl2:
                    clientUrl = ampUrl2
                else:
                    raise Exception('未找到客户端登录地址')
                res = self.session.get(clientUrl)
                self.campus_host = re.findall('\w{4,5}\:\/\/.*?\/', clientUrl)[0]
                self.login_url = res.url
                self.login_host = re.findall('\w{4,5}\:\/\/.*?\/', res.url)[0]
                self.login_type = joinType
                break
        if flag == False:
            raise Exception(self.schoolName + '不存在或未加入今日校园')

    # 通过登陆url判断采用哪种登陆方式
    def checkLogin(self):
        if self.login_type == 'CLOUD':
            self.loginEntity = iapLogin(self.username, self.password,
                                        self.login_url, self.login_host,
                                        self.session)
            self.session.cookies = self.loginEntity.login()
        elif self.login_url.find('kmu.edu.cn') != -1:
            raise Exception('请联系开发者适配登陆')
        else:
            self.loginEntity = casLogin(self.username, self.password,
                                        self.login_url, self.login_host,
                                        self.session)
            self.session.cookies = self.loginEntity.login()

    # 本地化登陆
    def login(self):
        # 获取学校登陆地址
        self.getLoginUrlBySchoolName()
        self.checkLogin()
