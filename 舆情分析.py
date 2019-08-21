

# -*- encoding: utf-8 -*-


import pandas as pd
import urllib3
import json
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from urllib.request import quote
pd.set_option('mode.chained_assignment', None)

class company:
    company_name=""
    title_list=[]
    href_list=[]
    abst_list=[]
    src_time_list=[]
    news_num=0
    def __init__(self,company_name):
        self.company_name=company_name


def get_data_from_chinaso(company_list):
    #爬取新闻数据
    chinaso_url="http://news.chinaso.com/newssearch.htm?q="
    for company in company_list:
        company_name=str(company.company_name)
        pro_company_name=quote(company_name) #编码中文字符
        page=1
        while True:
            time.sleep(2)
            tmp_url=chinaso_url+str(pro_company_name)+"&page="+str(page)
            print(tmp_url)
            print("当前搜索单位:"+company_name)
            print("当前搜索页数:"+str(page))
            web = urlopen(tmp_url)  # 打开网址
            html = web.read()  # 读取网页内容，保存到html中
            bs0bj = BeautifulSoup(html, features="lxml",from_encoding="utf-8")  # 创建一个beautifulsoup的类
            news_links = bs0bj.select('li[class="reItem"]')  # 通过标签筛选文字信息
            for link in news_links:
                title=str(link.find("a").get_text()) #标题
                href=link.find("a").get("href") #链接
                abst=link.select('div[class="reNewsWrapper clearfix"]') #摘要
                if len(abst)>0:
                    abst=str(abst[0].find('p').get_text().strip().replace("\n","").replace(" ",""))
                else:
                    abst=""  #有些新闻的摘要只有图
                src_time=link.select('p[class="snapshot"]')
                if len(src_time)>0:
                    src_time = link.select('p[class="snapshot"]')[0].find('span').get_text()
                else:
                    src_time=""
                if company_name in title or company_name in abst:
                    company.title_list.append(title)
                    company.href_list.append(href)
                    company.abst_list.append(abst)
                    company.src_time_list.append(src_time)
                    company.news_num+=1
            #print(bs0bj.select('a[_dom_name="next"]'))
            if len(bs0bj.select('a[_dom_name="next"]'))==0:
                print("没有下一页了")
                break
            else:
                page+=1


def write_excel(company_list,filename):
    ziduan = ["单位", "类别", "新闻标题", "新闻摘要", "时间和来源", "链接"]
    df=pd.DataFrame([[0,0,0,0,0,0]],columns=ziduan)

    cnt=0
    for company in company_list:
        for i in range(company.news_num):

            df.loc[cnt]=[company.company_name,"",company.title_list[i],company.abst_list[i],company.src_time_list[i],company.href_list[i]]
            cnt+=1
    newfilename=filename.split(".")[0]+"_舆情分析.xlsx"
    df.to_excel(newfilename,index=False)

    return newfilename

def get_sentiment_analysis_url():
    #使用百度情感分析API
    access_token = '24.85949d2357c904de59e59214010c6213.2592000.1568789179.282335-17041251'
    url = 'https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?access_token=' + access_token
    return url


def sentiment_analysis(target,analysis_url):
    #情感分析模块
    # 输入文本，输出情感极性
    params = {'text': target}
    if target=="":
        return 1
    # 进行json转换的时候，encode编码格式不指定也不会出错
    http = urllib3.PoolManager()
    encoded_data = json.dumps(params).encode('utf8')
    request = http.request('POST',
                           analysis_url,
                           body=encoded_data,
                           headers={'Content-Type': 'application/json'})
    # 注意编码格式
    result = str(request.data, 'GBK')
    a = json.loads(result)

    if "error_msg" in a.keys():
        print(a["error_msg"])
        return "error"
    elif "items" in a.keys():
        items = a['items'][0]
        return items["sentiment"]

def analysis_and_writeback(filename,company_list):
    # 调用情感分析API,并把情感分析结果写回excel
    analysis_url=get_sentiment_analysis_url()
    df = pd.read_excel(filename, encoding="utf-8")
    total=df.shape[0]
    length=len(company_list)
    cnt=0
    for i in range(length):
        cur_company=company_list[i]
        for k in range(cur_company.news_num):
            result1=sentiment_analysis(cur_company.title_list[k],analysis_url)
            if result1=="error":
                return 0
            time.sleep(2)  # 每查询一次暂停两秒，因为API有QPS限制
            result2=sentiment_analysis(cur_company.abst_list[k],analysis_url)
            if result1==0 or result2==0:
                result="负面"
            else:
                result = "中性/正面"
            df["类别"][cnt]=result
            cnt+=1
            print("分析进度:"+str(cnt)+"/"+str(total))
    df.to_excel(filename,index=False)
    return 1


if __name__=="__main__":
    print("请输入要查询的企业列表所在的txt文件：")
    #filename=str(input())
    filename="input.txt"
    company_list=[]
    with open(filename,'r',encoding="utf-8-sig") as f1:
        all=f1.readlines()
        for x in all:
            x=x.strip().replace("\n","")
            Com=company(x)
            company_list.append(Com)



    #get_data_from_sougou(company_list)
    print("正在采集数据...")
    get_data_from_chinaso(company_list)
    print("数据采集完成。正在写入数据...")
    newfilename=write_excel(company_list,filename)
    print("数据写入完成，正在分析数据...")

    res=analysis_and_writeback(newfilename,company_list)
    if res==1:
        print("数据分析完成，文件已保存。")
    else:
        print("分析出错，错误信息如上。")

