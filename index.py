import yaml

from todayLoginService import TodayLoginService
from actions.autoSign import AutoSign
from actions.collection import Collection
from actions.workLog import workLog
from actions.sleepCheck import sleepCheck
from actions.rlMessage import RlMessage
from login.Utils import Utils


def getYmlConfig(yaml_file='config.yml'):
    file = open(yaml_file, 'r', encoding="utf-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    return dict(config)


def main():
    config = getYmlConfig()
    for index, user in enumerate(config['users']):
        print(f'{Utils.getAsiaTime()} 第{index + 1}个用户正在执行...')
        rl = RlMessage(user['user']['sendKey'], config['emailApiUrl'], config['myQmsgKey'], config['sendType'])
        if config['debug']:
            msg = working(user)
        else:
            try:
                msg = working(user)
            except Exception as e:
                msg = str(e)
                print(Utils.getAsiaTime() + ' ' + msg)
                msg = rl.send('error', msg)
                print(Utils.getAsiaTime() + ' ' + msg)
                continue
        print(Utils.getAsiaTime() + ' ' + msg)
        msg = Utils.getAsiaTime() + ' ' + rl.send('maybe', msg)
        print(msg)
        print(f"{Utils.getAsiaTime()} 第{index + 1}个用户执行完毕！")


def working(user):
    print(f'{Utils.getAsiaTime()} 正在获取登录地址')
    today = TodayLoginService(user['user'])
    print(f'{Utils.getAsiaTime()} 正在登录ing')
    today.login()
    # 登陆成功，通过type判断当前属于 信息收集、签到、查寝
    # 信息收集
    if user['user']['type'] == 0:
        # 以下代码是信息收集的代码
        print(f'{Utils.getAsiaTime()} 正在进行“信息收集”...')
        collection = Collection(today, user['user'])
        collection.queryForm()
        collection.fillForm()
        msg = collection.submitForm()
        return msg
    elif user['user']['type'] == 1:
        # 以下代码是签到的代码
        print(f'{Utils.getAsiaTime()} 正在进行“签到”...')
        sign = AutoSign(today, user['user'])
        sign.getUnSignTask()
        sign.getDetailTask()
        sign.fillForm()
        msg = sign.submitForm()
        return msg
    elif user['user']['type'] == 2:
        # 以下代码是查寝的代码
        print(f'{Utils.getAsiaTime()} 正在进行“查寝”...')
        check = sleepCheck(today, user['user'])
        check.getUnSignedTasks()
        check.getDetailTask()
        check.fillForm()
        msg = check.submitForm()
        return msg
    elif user['user']['type'] == 3:
        # 以下代码是工作日志的代码
        print(f'{Utils.getAsiaTime()} 正在进行“工作日志”...')
        work = workLog(today, user['user'])
        work.checkHasLog()
        work.getFormsByWids()
        work.fillForms()
        msg = work.submitForms()
        print(msg)
        return msg
    else:
        raise Exception('任务类型出错，请检查您的user的type')


# 阿里云的入口函数
def handler(event, context):
    main()


# 腾讯云的入口函数
def main_handler(event, context):
    main()
    return 'ok'


if __name__ == '__main__':
    main()
