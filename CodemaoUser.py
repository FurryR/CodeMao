#no desp
import json
import requests
from requests.utils import cookiejar_from_dict, dict_from_cookiejar

User_Agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18363'

web = requests.session()

class CodemaoShequError(Exception):
    pass

class CodemaoUser:
    '''OOP Codemao user'''
    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': User_Agent
    }

    def __init__(self, username=None, password=None):
        self.cookies = {}
        if username and password != None:
            self.username = username
            self.password = password
            self.login(self.username, self.password)
        else:
            self.username = None
            self.password = None

    def login(self, Username, Password):
        try:
            data = '{"identity":"' + Username + '","password":"' + Password + '","pid":"65edCTyg"}'
            ret = web.post("https://api.codemao.cn/tiger/v3/web/accounts/login", 
                            data, headers=self.headers)
        except requests.RequestException as error:
            raise CodemaoShequError("login failed,reason:" + str(error))

        if ret.status_code != 200:
            raise CodemaoShequError("login failed,reason:username/password error")

        self.cookies = dict_from_cookiejar(ret.cookies)
    
    def get_cookie(self):
        keys = web.cookies.keys()
        values = web.cookies.values()
        cookie = ""
        for x in range(len(keys)):
            cookie = cookie + keys[x] + "=" + values[x] + ";"
        return cookie

    def set_cookie(self, cookie):
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
            raise CodemaoShequError('cookie select failed')

    def verify_cookie(self, cookie=web.cookies):
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
                           headers=self.headers, cookies=cookie_dict)

        if ret.status_code == 200:
            return True
        return False

    def get_my_info(self):
        ret = requests.get("https://api.codemao.cn/web/users/details", headers=self.headers, cookies=self.cookies)
        info1 = ret.json()
        ret = requests.get("https://api.codemao.cn/api/user/info", headers=self.headers, cookies=self.cookies)
        info2 = ret.json()
        info1['doing'] = info2['data']['userInfo']['doing']
        info1['level'] = info2['data']['userInfo']['level']
        info1['telephone'] = info2['data']['userInfo']['telephone']
        info1['email'] = info2['data']['userInfo']['email']
        info1['qq'] = info2['data']['userInfo']['qq']
        return info1

    def __getattr__(self, name):
        info_list = [
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
        ret = web.get("https://api.codemao.cn/api/user/info/detail/" + str(uid), headers=self.headers)
        info = ret.json()
        info = info['data']['userInfo']
        info['user']['description'] = info['user']['description'].replace('\\n', '\n')
        info['user']['doing'] = info['user']['doing'].replace('\\n', '\n')
        info['user']['preview_work_src'] = 'https://shequ.codemao.cn/work/' + str(info['user']['preview_work_id'])
        return info
    
    def set_my_info(self, nickname, sex, description, fullname, birthday, avatar_url):
        try:

            headers = {"User_Agent": User_Agent,
                       "Content-Type": "application/json;charset=UTF-8"}
            data = '{"nickname":"%s","description":"%s","sex": %d,"fullname":"%s","birthday": %d,"avatar_url":"%s"}' \
                   % (nickname,description,sex,fullname,birthday,avatar_url)

            ret = web.patch('https://api.codemao.cn/tiger/v3/web/accounts/info',
                            data=data.encode('utf-8'), headers=headers)

            if ret.status_code != 204:
                raise CodemaoShequError(ret.text)
            return True
        except BaseException as error:
            raise CodemaoShequError(str(error))
