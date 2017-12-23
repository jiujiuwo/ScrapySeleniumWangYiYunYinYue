# -*- coding: utf-8 -*-
"""
Created on Thu Dec 21 14:29:03 2017

@author: 李海峰
"""

import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import codecs
import json

class UserSongListSpider(scrapy.Spider):
  
    name = 'UserSongListSpider'
    
    #scrapy的框架模式，先定义请求，然后异步执行，然后执行回调函数
    def start_requests(self):
        urls = ['https://music.163.com/user/home?id=269241661',]
        for url in urls:
            yield scrapy.Request(url=url,callback=self.parse)

    def parseUserInfo(self,response):
        #爬取用户信息
        userInfo = {}
        userInfo['name'] = response.xpath('//span[@class="tit f-ff2 s-fc0 f-thide"]/text()').extract_first(default='not-fpund')
        userInfo['age'] = response.xpath('//span[@id="age"]/span/text()').extract_first(default='not-fpund')
        userInfo['quote'] = response.xpath('//div[@class="inf s-fc3 f-brk"]/text()').extract_first(default='not-fpund')
        userInfo['address'] = response.xpath('//div[@class="inf s-fc3"]/span/text()').extract_first(default='not-fpund').split('：')[1]
        userInfo['userId'] = response.url.split('=')[-1]
        if not response.xpath('//i[@class="icn u-icn u-icn-01"]')  is None:
            userInfo['sex'] = '男'
        else:
            userInfo['sex'] = '女'
        self.log(userInfo)
        return userInfo

    def parseCreateSongList(self,response,userInfo):
         #爬取用户创建的歌单信息
        userCreateSongListLists = []

        for songList in response.xpath('.//ul[@id="cBox"]/li'):
            #self.log(songList.extract())
            songListInfo = {}
            songListInfo['userId'] = userInfo['userId']
            songListInfo['title'] = songList.xpath('.//a[@class="tit f-thide s-fc0"]/text()').extract_first()
            songListInfo['href'] = songList.xpath('.//a[@class="tit f-thide s-fc0"]').xpath('@href').extract_first()
            songListInfo['id'] = songListInfo['href'].split('=')[1]
            userCreateSongListLists.append(songListInfo)
            self.log(songListInfo)
        self.log(userCreateSongListLists)
        return userCreateSongListLists
    
    def parseSaveSongList(self,response,userInfo):
         #爬取用户收藏的歌单信息
        userSaveSongListLists = []

        for songList in response.xpath('.//ul[@id="sBox"]/li'):
            #self.log(songList.extract())
            songListInfo = {}
            songListInfo['userId'] = userInfo['userId']
            songListInfo['title'] = songList.xpath('.//a[@class="tit f-thide s-fc0"]/text()').extract_first()

            #取属性值的xpath的用法
            songListInfo['href'] = songList.xpath('.//a[@class="tit f-thide s-fc0"]').xpath('@href').extract_first()
            songListInfo['id'] = songListInfo['href'].split('=')[1]
            userSaveSongListLists.append(songListInfo)
            self.log(songListInfo)
        self.log(userSaveSongListLists)
        return userSaveSongListLists

    #请求之后的回调函数
    def parse(self,response):
        driver = webdriver.Chrome()
        driver.get(response.url)
        wait = WebDriverWait(driver, 2)  
        driver.switch_to_frame("contentFrame")
        response = response.replace(body=driver.page_source)
        file_name = 'UserSongListSpider_'+response.url.split('=')[-1]+'.txt'

        #爬取用户基本信息
        userInfo = self.parseUserInfo(response= response)

        #爬取用户创建的歌单信息
        userCreateSongLists = self.parseCreateSongList(response = response,userInfo=userInfo)
        #爬取用户收藏的歌单信息
        userSaveSongLists = self.parseSaveSongList(response = response,userInfo = userInfo)
        #汇总用户信息并保存
        userSongListSpider = {'userInfo':userInfo,'userCreateSongLists':userCreateSongLists,'userSaveSongLists':userSaveSongLists}

        f = codecs.open(file_name,'w','utf-8')
        f.write(json.dumps(userSongListSpider))
        f.close()
        self.log('Saved file %s ' % file_name)       
