from bs4 import BeautifulSoup
from AutoSign import Login
import re

HomeWorkDic={}#存储 课程:作业
Param="https://sso.scnu.edu.cn/AccountService/openapi/login.html?response_type=code&client_id=3f86b543c74eed80e7d72658699f6345&redirect_url=https%3A%2F%2Fmoodle.scnu.edu.cn%2Fauth%2Fsso%2Flogin.php"#应用id与跳转位置

s=Login(Param)


ClassURL="https://moodle.scnu.edu.cn/course/view.php?id="
HWURL="https://moodle.scnu.edu.cn/mod/assign/view.php?id=99803"
ClassDic={
    "计算机网络":"9406",
    "多媒体技术":"6894",
    "WEB开发基础":"5469",
    "Python语言程序设计":"5449"
}
for i in ClassDic:
    # print("\n",i,"\n")#打印标题
    HomeWorkDic[i]=""#存储标题
    res6=s.get(ClassURL+ClassDic[i])#进入课程
    page=BeautifulSoup(res6.content.decode(),"lxml")

    #匹配作业的url
    HomeWorkList=page.find_all(name='a',attrs={"href":re.compile(r'https:\/\/moodle\.scnu\.edu\.cn\/mod\/assign\/view\.php\?id=')}) 
    # print(kksk[0].get("href"))

    #匹配出一堆作业链接，再循环
    for f in range(0,len(HomeWorkList)):

        #进入作业页面
        HomeWorkPage=s.get(HomeWorkList[f].get("href"))
        LoadHomwWorkPage=BeautifulSoup(HomeWorkPage.content.decode(),"lxml")

        Wok0=LoadHomwWorkPage.find(name="h2")#作业标题
        Wok1=LoadHomwWorkPage.find(name="a",attrs={"href":re.compile(r"https:\/\/moodle\.scnu\.edu\.cn\/pluginfile\.php\/[0-9]*\/mod_assign")})#匹配文件及链接
        Wok2=LoadHomwWorkPage.find(name="div",attrs={"id":"intro"})#匹配作业内容
        Wok3=LoadHomwWorkPage.find_all(name='tr')#获取作业状态[2],截止时间

        # print(Wok0.text)
        HomeWorkDic[i]+=Wok0.text

        #下面两项print作业的文件的链接或者直接内容
        try:
            # print(Wok1.text,"链接:",Wok1['href'])
            HomeWorkDic[i]+=(Wok1.text+"链接:"+Wok1['href'])
        except Exception as e :
            pass
        try:
            # print(Wok2.text)
            HomeWorkDic[i]+=(Wok2.text)
        except Exception as e :
            pass

        # print(Wok3[2].text)#截止时间
        HomeWorkDic[i]+=Wok3[2].text
print(HomeWorkDic)