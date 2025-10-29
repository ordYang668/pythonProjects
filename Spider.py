import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from  selenium.webdriver.edge.service import Service

##浏览器驱动初始化
op=webdriver.EdgeOptions()
op.add_experimental_option('detach',True)
###驱动器地址
driver_path=Service('D:msedgedriver.exe')
browser=webdriver.Edge(service=driver_path,options=op)

'''假设网址列表里有如下网站,所有的网站的都是搜索china为例
https://search.bilibili.com/all?keyword=china&from_source=webtop_search&spm_id_from=333.1007&search_source=5
https://so.toutiao.com/search?dvpf=pc&source=input&keyword=china
https://newssearch.chinadaily.com.cn/en/search?query=china
'''
##录入网址(我测试的网址都是搜索关键字“china”为例)
url=input('请输入要爬取的网址：')
# 打开网页
browser.get(url)
#休息五秒先
time.sleep(5)
##获取页面HTML代码
content=browser.page_source
##beautifulsoup规范化获取的页面(其实就是content里代码比较乱，用beautifulsoup把content格式化成html形式)
Soup=BeautifulSoup(content,'html.parser')
##将规范后的内容变成字符串并输出
# soup=Soup.prettify()
# print(soup)
flag_self = 0
#建立一个fast集合列表来存储标签的name以及class
fast_list = set()

##下面代码先定位到有china的标签，再根据china的标签将其父亲节点以及父亲的兄弟节点遍历，以得到其中内容
##先是找到包含china的标签
for i in Soup.find_all(string=re.compile("ina"), name=True):
    ##在找china标签的父亲标签
    for j in i.parents:
        #把父亲标签name记录下来
        parent_name = j.name
        try:
            ##找到父亲标签的class属性，并记录下来
            parent_class = j['class']
            #做一些处理使其转换成字符串
            parent_class = ' '.join(parent_class)
            ##找完父亲找父亲的下一个(next)的兄弟（也就是叔叔伯伯），这时，只有name和class属性都和父亲一样的叔叔伯伯标签才能被记录下来，否则就except弹出去
            for i in j.find_next_siblings(parent_name, parent_class):
                ##我们用一个集合：fast_list以存放记录过的标签，以防止重复存放
                if (len(fast_list) != 0 and (str(j.name) + '_' + str(parent_class)) in fast_list):
                    break
                #对于每一类标签的第一个内容，我们采用以下处理

                if flag_self == 0:
                    # 找到正文，并分割不同种类标签
                    print('标签种类分割线——————————————————————————————\n' + j.text)
                    # #找到连接
                    #图片链接
                    for k in j.find_all(name='img'):
                        print(k['src'])
                    # 跳转链接
                    for k in j.find_all(href=True):
                        print(k['href'])
                    flag_self = 1
                #遍历过就记录下
                fast_value = str(j.name) + '_' + str(parent_class)

                #对于每一类的第一个标签以后的标签，我们采用以下方法记录

                # 得到正文
                print(i.text)
                # 得到图片以及跳转链接
                for k in i.find_all(name='img'):
                    print(k['src'])
                for k in i.find_all(href=True):
                    print(k['href'])
                print('----------------------------------------------------------------------------')

            flag_self = 0
            #遍历过同一类标签后就将value添加到集合列表中
            fast_list.add(fast_value)
        except:
            continue
