## 今日校园免费签到打卡平台

> 项目前身： `fuckTodayStudy`，`python`版的`fuckTodayStudy`项目已经停止维护很久了，git上目前主要有基于`fuckTodayStudy`项目的魔改项目[`ruoli-sign-optimization`](https://github.com/IceTiki/ruoli-sign-optimization) 同时我也为其提供了`apple`以做签到时弹出的图片验证码识别，但是由于很多人非科班出身，也没经历为了一个打卡任务学习`python`这门语言，因此在项目重构了，基于`java`技术栈，前端采用`vue`，基本上重构完成

<a href="https://itstar.ruoli.cc">点击这里进入</a>


#### 邀请码


> ITStarYYDS

#### 目前支持学校

- [x] 宜宾学院

- [x] 武汉船舶职业技术学院
- [x] 安徽机电职业技术学院 
- [x] 惠州城市职业学院  
- [x] 沈阳音乐学院 
- [x] 浙江商业职业技术学院 
- [x] 河南大学 
- [x] 吉林工程职业学院  
- [ ] 更多学校欢迎大家提`Issue`

#### 目前支持的打卡类型

- [x] 🥪信息收集
- [x] 🍺签到
- [ ] ☠️查寝
- [ ] ☠️工作日志
- [ ] 更多类型欢迎大家PR

#### 目前免费使用方式

- 通过邀请码注册到本平台即可获得`10.00`积分
- 一个任务一次执行成功将消耗`1.00`积分
- 获取积分方式
  - 通过个人中心获取邀请码，邀请新人注册本平台即可双方都得到`10.00`积分
  - 更多获取方式待定

#### 平台工作逻辑

模拟用户进行今日校园账号登录，然后获取表单信息，并且模拟用户进行表单选项勾选以及填写，最后完成提交任务

#### 建议

若您有任何建议请加群反馈！

#### 免责声明

您使用本平台造成的一切后果由您自己承担，与本平台无关。

#### 平台使用简单说明

1. 通过邀请码注册
2. 添加您的今日校园账号
3. 添加打卡定时任务

等待系统自动执行或您在`任务管理`中手动执行

#### 平台使用细节

1. 添加完成任务后若在当前时间刚好满足您设置的执行时间、次数、周期等参数要求，会自动放入线程池中进行`打卡`，而无需您手动去`任务管理`板块点击`执行`按钮
2. 自动执行任务时，若检测到您任务已经完成，会返回相关的提示信息并返回；在`任务管理`板块手动执行时，会不管任务是否完成强制将完成整套逻辑，最后返回今日校园提交表单后返回的信息
3. 平台后台线程池为10，基于目前用户基数是完全足够的，若之后不足可能会采取各位赞助的方式来完成更多集群的部署
4. 添加任务时的经纬度，请在其中给出的网址中查询，查询后选择一个位置后右上角会出现您选择的位置的经纬度，诸如`104.622113,28.802129`，请将`104.622113`填入经度，将`28.802129`填入纬度。
5. 添加任务时，若您在今日校园上的表单信息中有地址选择框，如`xx省/xx市/xx县/xx镇`之类的，只需将`xx省/xx市/xx县/xx镇`一起填入平台即可。
6. 更多的使用细节待补充，QQ群：`734468929`期待更多人一起探讨
