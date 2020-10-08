#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import json
import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'  # 默认浏览器标识

web = requests.session()  # 连接站点，session保持连接

class CodemaoShequError(Exception):
    '''编程猫社区异常'''
    pass

class CodemaoUser:
    '''编程猫用户信息'''
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': User_Agent
    }    # 编程猫社区特有协议头，必须要有这两个

    def __init__(self, username=None, password=None):
        """
        此类用于操作编程猫社区中的用户信息

        参数:
            usernmae  (str) 可选参数, 初始化时登录的用户名
            password  (str) 可选参数, 初始化时登录的密码
        """
        self.cookies = {}
        if username and password != None:
            self.username = username
            self.password = password
            self.login(self.username, self.password)
        else:
            self.username = None
            self.password = None

    def login(self, Username, Password):
        """
        通过账号密码，获取用户的cookie，cookie作为用户登录到服务器的标识。
        获得cookie后在Codemao类销毁前所有子类均记录cookie
        参数详情：
            User(str) --- 提供用户名称
            Possword(str)  --- 提供用户密码

        返回:如果登录成功返回None，否则报错
        """
        try:
            # data = {'identity': Username, 'password': Password, 'pid': '65edCTyg'}  # 写请求数据
            data = '{"identity":"' + Username + '","password":"' + Password + '","pid":"65edCTyg"}'  # 写请求数据
            ret = web.post("https://api.codemao.cn/tiger/v3/web/accounts/login", 
                            data, headers=self.headers)
        except requests.RequestException as error:
            raise CodemaoShequError("登录失败原因：" + str(error))

        if ret.status_code != 200:
            raise CodemaoShequError("登录失败原因：账号密码错误！")

        self.cookies = dict_from_cookiejar(ret.cookies)
    
    def get_cookie(self):
        """
        若已设置或已登录用户可返回目前正在使用的cookie

        参数说明：
        返回：cookie(str)
        """
        keys = web.cookies.keys()
        values = web.cookies.values()
        cookie = ""
        for x in range(len(keys)):
            cookie = cookie + keys[x] + "=" + values[x] + ";"
        return cookie

    def set_cookie(self, cookie):
        """
        若已有cookie，请使用此函数设置cookie状态

        参数说明：
        cookie(str) --- 已有的cookie

        返回：设置成功返回None,失败报错
        """
        split1 = cookie.split(";")
        cookie_dict = {}
        for i in range(len(split1)):
            split2 = split1[i].split("=")

            if len(split2) != 2:
                continue
            cookie_dict[split2[0].strip()] = split2[1].strip()
        try:
            web.cookies.update(cookiejar_from_dict(cookie_dict))
        except requests.RequestException:
            raise CodemaoShequError('cookie设置失败')

    def ver_cookie(self, cookie=web.cookies):
        """
        如果你需要验证此cookie是否是可以登录编程猫的，请使用此函数验证

        参数说明：
        cookie(str) --- 可选，默认使用默认的cookie

        返回：是否成功登录(bool)   若网络原因直接报错
        """

        if cookie == web.cookies:
            keys = cookie.keys()
            values = cookie.values()
            cookie = ""
            for x in range(len(keys)):
                cookie = cookie + keys[x] + "=" + values[x] + "; "
            return cookie
        
        cookies = cookie.split(';')
        cookie_dict = {}
        for cookie in cookies:
            if not cookie:
                continue
            key, value = cookie.split('=')
            cookie_dict[key] = value
        
        ret = requests.get("https://shequ.codemao.cn/user/",
                           headers=self.headers, cookies=cookie_dict)  # 这里不能用web.get(),web是在保持现有的连接下，我们要使用新的连接来验证 默认使用web的cookie

        if ret.status_code == 200:
            return True
        return False

    def get_my_info(self):
        """
        获取目前登录用户的信息，如果用户未登录则会返回一个空的字典，或者报错。

        返回：用户信息(dict) --- 用户的信息
        用户未设置则返回空文本
        数据key --  数据分类 -- 数据类型
        id   --  用户ID --  int
        nickname -- 用户昵称 -- str
        avatar_url -- 用户头像URL -- str
        email  --  用户邮箱 -- str
        gold   --   用户金币数 -- int
        qq   --  用户QQ  -- str
        real_name  --  用户真名 -- str
        sex   --  用户性别 -- str(男MALE  女FEMALE)
        username -- 用户名 -- str
        voice_forbidden -- 已被禁言 -- bool
        birthday -- 生日 -- int (时间戳)
        description -- 简介 -- str
        phone_number -- 加掩码的电话 -- str
        create_time -- 用户创建时间 -- int(时间戳)
        oauths -- 用户账户绑定情况 -- list(列表内有数组见下)
         |       原数据：[ {'id':1,'name':'wechat','is_bound':False} , ...]
         |       翻译： id -- 1:微信 2:QQ 3:优学派 4:国家教育资源公共服务平台 5:豹豹龙官网 6:新华文轩出版传媒 7:云知声 8.icollege远程教育平台 9.dledc? 10.apple? 11.我time网 12.中国招商银行 13:编程猫-新零售
         |              name -- 上述对应的名称     is_bound -- 是否绑定
        has_password -- 用户有密码 -- bool
        user_type -- 用户类型 -- int (未知，盲猜有普通用户、管理员之分)
        show_guide_flag  -- 展示向导标志 -- int (未知，盲猜引导页面)
        doing -- “我正在做什么”列表 -- str
        level -- 用户等级 -- int
        telephone -- 绑定电话 -- str
        """
        ret = requests.get("https://api.codemao.cn/web/users/details", headers=self.headers, cookies=self.cookies)  # 返回json
        info1 = ret.json()  # 解码
        ret = requests.get("https://api.codemao.cn/api/user/info", headers=self.headers, cookies=self.cookies)  # 返回json
        info2 = ret.json()  # 解码
        info1['doing'] = info2['data']['userInfo']['doing']
        info1['level'] = info2['data']['userInfo']['level']
        info1['telephone'] = info2['data']['userInfo']['telephone']
        info1['email'] = info2['data']['userInfo']['email']
        info1['qq'] = info2['data']['userInfo']['qq']
        return info1

    def __getattr__(self, name):
        '''获取用户信息
        像这样：info_xxx'''
        info_list = [    #属性列表
            'id', 'nickname', 'avatar_url', 'email', 'gold',
            'qq', 'real_name', 'sex', 'username', 'voice_forbidden',
            'birthday', 'description', 'phone_number', 'create_time', 'oauths',
            'has_password', 'user_type', 'show_guide_flag', 'doing', 'level',
            'telephone'
        ]
        if name.startswith('info_'):
            if name[5:] in info_list:
                return self.get_my_info()[name[5:]]
        raise AttributeError(repr(self.__class__.__name__) + ' object has no attribute ' + repr(name))

    def get_other_info(self, uid):
        """
        获取别人或自己的用户信息
        如果网络原因则会触发错误

        参数说明：uid(int) -- 用户id
        返回说明：用户信息(dict) -- 返回存有用户信息的列表

        数据key --  数据分类 -- 数据类型
        isFollowing -- 我是否已关注 -- int
        collectionTimes -- 收藏数 -- int
        forkedTimes -- 再创作数 -- int
        praiseTimes -- 获赞数 -- int
        viewTimes -- 被浏览次数 -- int
        user -- 用户信息 -- dict 如下：
        |   id -- 用户id ；  nickname -- 用户昵称 ；  sex -- 性别(int 0女 1男) ； description -- 描述 ；doing -- 正在做的 ;
        |   avatar -- 头像地址 ； level -- 等级 ；preview_work_id -- 展示作品id ； preview_work_src --  展示作品地址
        work -- 展示作品详情 -- dict 如下：
        |   id -- 作品id   name -- 作品名称   preview -- 作品预览图

        """
        ret = web.get("https://api.codemao.cn/api/user/info/detail/" + str(uid), headers=self.headers)  # 返回json
        info = ret.json()  # 解码
        info = info['data']['userInfo']
        info['user']['description'] = info['user']['description'].replace('\\n', '\n')
        info['user']['doing'] = info['user']['doing'].replace('\\n', '\n')
        info['user']['preview_work_src'] = 'https://shequ.codemao.cn/work/' + str(info['user']['preview_work_id'])
        return info
    
    def set_my_info(self, nickname, sex, description, fullname, birthday, avatar_url):
        """
        更改自己的设置

        参数说明：
        nickname(str) -- 昵称
        sex(int) -- 性别(0女 1男)
        description(str) -- 描述
        fullname(str) -- 真实名称
        birthday(int) -- 生日(时间戳)
        avatar_url(str) -- 头像网址

        返回：成功返回None，失败报错
        """
        try:

            headers = {"User_Agent": User_Agent,
                       "Content-Type": "application/json;charset=UTF-8"}  # 编程猫社区特有协议头，必须要有这两个
            data = '{"nickname":"%s","description":"%s","sex": %d,"fullname":"%s","birthday": %d,"avatar_url":"%s"}' \
                   % (nickname,description,sex,fullname,birthday,avatar_url)

            ret = web.patch('https://api.codemao.cn/tiger/v3/web/accounts/info',
                            data=data.encode('utf-8'), headers=headers)

            if ret.status_code != 204:
                raise CodemaoShequError(ret.text)
            return True
        except BaseException as error:
            raise CodemaoShequError(str(error))
