import requests
# from requests.cookies import RequestsCookieJar
from urllib import parse
from TencenOCR import *
import json
import random
from bs4 import BeautifulSoup
import os



CheckRamCodeUrl = "https://sso.scnu.edu.cn/AccountService/user/checkrandom.html"
RanCodeUrl = "https://sso.scnu.edu.cn/AccountService/user/rancode.jpg"
AuthUrl = "https://sso.scnu.edu.cn/AccountService/openapi/auth"  # 验证验证码的url

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
    #血的教训
    # "redirect_url": "https://moodle.scnu.edu.cn/auth/sso/login.php",
    "redirect_url":"",
    "jump": None,
}

def Login(Param):
    url = Param
    Head['Referer']=url
    Param=Param[Param.index('?')+1:]
    kksk= Param.split('&')

    for i in kksk:
        ParamList=i.split('=')
        
        #client_id 后可能还有参数，比如实验室#/auth/redirect
        FormDict[ParamList[0]]=ParamList[1][:32]

    
    #Param="https://sso.scnu.edu.cn/AccountService/openapi/login.html?response_type=code&redirect_url=https%3A%2F%2Fssp.scnu.edu.cn%2FLogBySso.aspx&client_id=79808d49dae212d7dcd12d7e0d25173b"

#创建session
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
    while flag:
        # 用第一次请求的cookie请求验证码(同时刷新验证码)
        res2 = s.get(RanCodeUrl+"?m="+str(random.random()*10),cookies="")
        # res2=requests.get(RanCodeUrl+"?m="+str(random.random()*10),cookies="")

        # 获得图片二进制
        try:
            with open("RandomCode.jpg", "wb") as f:
                # 把验证码图片写入本地文件
                print("Got recapcha Img")
                f.write(res2.content)
        except Exception as e:
            print("====出错====")
            print(e)
        # 调用腾讯OCR
        print("Tencent OCR invoke")
        RamCode = Recognise("Randomcode.jpg")

        RamCode = RamCode.replace(" ", "")  # 去空格
        print(RamCode)

        FormData_RamCode = {"random": RamCode}
        # 用获取验证码时的cookies提交验证码
        # checkramdom.html
        res3 = s.post(CheckRamCodeUrl,data=FormData_RamCode)
        print(res3.content.decode())
        if(res3.content.decode() != "true"):
            continue
        # 验证码填入表单
        # COOKs['AuthForm']['rancode']=RamCode
        FormDict['rancode'] = RamCode
        flag = False

    # SetServer=SetCookies[Cookies_Server+7:Cookies_Server+23]
    # SetJsonID=SetCookies[Cookies_JSESSIONID+11:Cookies_JSESSIONID+43]


    # 下面开始提交学号，密码（通过验证
    FormDict['rancode'] = RamCode
    res4 = s.post(AuthUrl,headers=Head,data=FormDict,allow_redirects=False)
    
    if res4.status_code==302 or res4.status_code==303:
        kksk=res4.headers['Location']
        
        #出错消息
        if "msgcode" in kksk:
            a=kksk.index("msgcode")
            b=kksk.index("&",a)
            print(parse.unquote(kksk[a+8:b]))
            os._exit(0)
        print("Login success") 

    # return res4#登录成功后的request,code应该是302/303,继续请求Respond Heade中的location
    res5=s.get(res4.headers['Location'])#请求location
    #print(res4.headers['Location'])
    #可能需要获取?code
    return (s,res4.headers['Location'])