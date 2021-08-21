import requests
from PIL import Image
import matplotlib.pyplot as matpyplot
from urllib import parse
import json
import random
from bs4 import BeautifulSoup
import sys

CheckRamCodeUrl = "https://sso.scnu.edu.cn/AccountService/user/checkrandom.html"
RanCodeUrl = "https://sso.scnu.edu.cn/AccountService/user/rancode.jpg"
AuthUrl = "https://sso.scnu.edu.cn/AccountService/openapi/auth" 
LoginUrl="https://sso.scnu.edu.cn/AccountService/user/login.html"
Head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Referer": "",
}
FormDict = {
    "account": "",#学号
    "password": "",#密码
    "rancode": None,
    "client_id": "",
    "response_type": "",
    "redirect_url": "",
    "jump": None,
}


def Login(TargetUrl):
    '''
    统一身份认证,返回跳转后的session
    '''
    if(len(FormDict["account"])==0 or len(FormDict["password"])==0):
        #手动输入吧
        print("账号密码为空，请在AutoSign.py的第21行输入")
        sys.exit()
    print("将使用 ",FormDict["account"]," 登录。")

    url = TargetUrl
    Head['Referer'] = url
    Param = TargetUrl[TargetUrl.index('?')+1:]
    kksk = Param.split('&')

    for i in kksk:
        ParamList = i.split('=')
        FormDict[ParamList[0]] = ParamList[1]

    # Param="https://sso.scnu.edu.cn/AccountService/openapi/login.html?response_type=code&redirect_url=https%3A%2F%2Fssp.scnu.edu.cn%2FLogBySso.aspx&client_id=79808d49dae212d7dcd12d7e0d25173b"

# 创建session
    s = requests.session()
    '''
    res1第一次打开sso(实际上可以直接要验证码，res1返回个登录的html而已)
    res2获取验证码（第一次刷新验证码)
    res3提交验证码
    res4提交学号、密码、验证码，返回头中有跳转location(code=)(response_type=code)
    res5打开励儒云
    '''

    # 第一次请求，打开sso
    res1 = s.get(url)
    flag = True
    matpyplot.ion()
    while flag:
        # 用第一次请求的cookie请求验证码(同时刷新验证码)
        res2 = s.get(RanCodeUrl+"?m="+str(random.random()*10), cookies="")
        # res2=requests.get(RanCodeUrl+"?m="+str(random.random()*10),cookies="")

        # 获得图片二进制
        # try:
        with open("RandomCode.jpg", "wb") as f:
            # 把验证码图片写入本地文件
            print("Got recapcha Img")
            f.write(res2.content)
        # except Exception as e:
        #     print("====出错====")
        #     print(e)


        RandomCodeimg = Image.open('RandomCode.jpg')
        matpyplot.figure("Code")
        matpyplot.imshow(RandomCodeimg)
        matpyplot.show()
        RamCode = input("请输入验证码:")
        matpyplot.clf()

        FormData_RamCode = {"random": RamCode}
        # 用获取验证码时的cookies提交验证码
        # checkramdom.html
        res3 = s.post(CheckRamCodeUrl, data=FormData_RamCode)
        rec3json=json.loads(res3.content.decode())
        print(rec3json)
        if(rec3json["msgcode"] != 0):
            continue
        # 验证码填入表单
        FormDict['rancode'] = RamCode
        matpyplot.clf()
        matpyplot.close('all')
        flag = False

    # 下面开始提交学号，密码（通过验证
    # FormDict['rancode'] = RamCode
    res4 = s.post(LoginUrl,headers=Head,data=FormDict,allow_redirects=False)
    res4Soup=BeautifulSoup(res4.content.decode(),'lxml')
    promptMsg=res4Soup.find_all(id="msgtext")
        # 出错消息
    if(len(promptMsg)!=0):
        print(promptMsg)

    if res4.status_code==302 or res4.status_code==303:
        res4RediretLocation=res4.headers['Location']
        # print('rediret location',res4RediretLocation)
        #../openapi/onekeyapp.html?app_id=18
            # os._exit(0)
        print("Login success") 

    # return res4#登录成功后的request,code应该是302/303,继续请求Respond Heade中的location

    res5=s.get(res4RediretLocation)#请求location
    return s
