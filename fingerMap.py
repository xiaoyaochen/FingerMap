#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   fingerMap.py
@Time    :   2021/05/26 16:29:54
@Author  :   coffee time 
@Version :   1.0
@Desc    :   web指纹识别工具
'''

# here put the import lib

from Wappalyzer import Wappalyzer,WebPage
import argparse,asyncio,time,aiohttp
from multiprocessing import Pool
import pandas as pd
from tqdm import tqdm
import logging
logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class fingerMap:
    def __init__(self,url_list,coroutineNum,Version):
        self.url_list = url_list
        self.coroutineNum = coroutineNum
        self.version = Version
        self.sema = asyncio.Semaphore(self.coroutineNum)
        self.loop = asyncio.get_event_loop()
        self.pool = Pool()
        self.result = []
        self.bar = tqdm(total=len(url_list))
        self.result = []

    #开始获取页面分析指纹信息
    async def run(self):
        futures = []
        for url in self.url_list:
            #异步获取网页信息
            future = asyncio.ensure_future(self.web_req(url))
            future.add_done_callback(self.call_bak)
            futures.append(future)
        self.async_session = await self.get_asyn_session()
        await asyncio.gather(*futures)
        await self.async_session.close()
        #阻塞指纹分析进程
        self.pool.close()
        self.pool.join()
        self.deel_result()

    #处理没有结果的url
    def deel_result(self):
        for url in self.url_list:
            self.result.append({"url":url})

    #创建异步请求session
    async def get_asyn_session(self):
        headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",}
        connector = aiohttp.TCPConnector(ssl=False)
        return aiohttp.ClientSession(headers=headers,connector=connector)


    #获取网页
    async def web_req(self,url):
        try:
            page = await WebPage.new_from_url_async(url,aiohttp_client_session=self.async_session)
            return page
        except Exception as e:
            self.bar.set_description(f"Processing {url},获取不到网页")
            self.bar.update(1)
            return None
    #获取网页进程回调函数
    def call_bak(self,webpage):
        webpage = webpage.result()
        # print(url_info.headers,url_info.html,url_info.scripts,url_info.meta)
        wappalyzer = Wappalyzer.latest()
        if webpage:
            webpage.parsed_html = None
        if self.version:
            self.pool.apply_async(wappalyzer.analyze_with_versions,args=(webpage,),callback=self.pro_call_bak)
        else:
            self.pool.apply_async(wappalyzer.analyze,args=(webpage,),callback=self.pro_call_bak)

    #指纹分析进程回调函数
    def pro_call_bak(self,finger):
        self.result.append({'url':finger[0],'title':finger[1],'status':finger[2],'finger':finger[3]})
        self.url_list.remove(finger[0])
        self.bar.set_description(f"Processing {finger}")
        self.bar.update(1)

def banner():
    print('''
        @Tool    :   fingerMap
        @Author  :   coffee time 
        @Version :   1.0
        @Desc    :   一款web指纹识别工具
        ''')


if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--coroutineNum',dest='CoroutineNum',type=int,default=100,help='协程并发数量')
    parser.add_argument('-f','--file',dest='File',help='url文件')
    parser.add_argument('-v','--version',dest='Version',help='是否查询版本,0为不查询，1为查询',default=0)
    parser.add_argument('-u','--url',dest='Url',help='url')
    args = parser.parse_args()
    File = args.File
    Url = args.Url
    Version = args.Version
    CoroutineNum = args.CoroutineNum
    url_list = []
    #读取url资产
    if File:
        print('开始批量扫描。。。')
        with open(File,'r',encoding='utf-8') as urls:
            for url in urls.readlines():
                url_list.append(url.strip())
    else:
        url_list.append(Url)

    #开始执行
    start = time.time()

    fingermap = fingerMap(url_list,CoroutineNum,Version)
    asyncio.run(fingermap.run())

    end = time.time()
    save_pd = pd.DataFrame.from_dict(fingermap.result)
    save_pd.to_csv(f'output/result{time.strftime("%Y%m%d%H%M%S",time.localtime())}.csv',index=False)
    logger.info('结束扫描,耗时：{}s'.format(end-start))
