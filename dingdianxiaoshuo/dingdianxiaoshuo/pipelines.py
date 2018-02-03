# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

#因为爬取整个网站时间较长，这里为了实现断点续传，我们把每个小说下载完成的
#章节地址存入数据库一个单独的集合里，记录已完成抓取的小说章节

from pymongo import MongoClient
from urllib import request
from bs4 import BeautifulSoup

#在pipeline中我们将实现下载每个小说，存入MongoDB数据库

class DingdianxiaoshuoPipeline(object):
    def process_item(self, item, spider):
        #print("马衍硕")
        #如果获取章节链接进行如下操作
        if "novel_section_urls" in item:
            # 获取Mongodb链接
            client = MongoClient("mongodb://127.0.0.1:27017")
            #连接数据库
            db =client.dingdian
            #获取小说名称
            novel_name=item['novel_name']
            #根据小说名字，使用集合，没有则创建
            novel=db[novel_name]

            #使用记录已抓取网页的集合，没有则创建
            section_url_downloaded_collection=db.section_url_collection

            index=0
            print("正在下载："+item["novel_name"])


            #根据小说每个章节的地址，下载小说各个章节
            for section_url in item['novel_section_urls']:

                #根据对应关系，找出章节名称
                section_name=item["section_url_And_section_name"][section_url]
                #如果将要下载的小说章节没有在section_url_collection集合中，也就是从未下载过，执行下载
                #否则跳过
                if  not section_url_downloaded_collection.find_one({"url":section_url}):
                    #使用urllib库获取网页HTML
                    response = request.Request(url=section_url)
                    download_response = request.urlopen(response)
                    download_html = download_response.read().decode('utf-8')
                    #利用BeautifulSoup对HTML进行处理，截取小说内容
                    soup_texts = BeautifulSoup(download_html, 'lxml')
                    content=soup_texts.find("dd",attrs={"id":"contents"}).getText()


                    #向Mongodb数据库插入下载完的小说章节内容
                    novel.insert({"novel_name": item['novel_name'], "novel_family": item['novel_family'],
                                  "novel_author":item['novel_author'], "novel_status":item['novel_status'],
                                  "section_name":section_name,
                                  "content": content})
                    index+=1
                    #下载完成，则将章节地址存入section_url_downloaded_collection集合
                    section_url_downloaded_collection.insert({"url":section_url})


        print("下载完成："+item['novel_name'])
        return item
