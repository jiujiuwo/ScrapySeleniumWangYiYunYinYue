#-*- coding: utf-8 -*-

import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import codecs
import json

class SongListSpider(scrapy.Spider):
	 
	 name = 'SongListSpider'

	 def start_requests(self):
	 	urls = ['https://music.163.com/playlist?id=368430295',]

	 	for url in urls:
	 		yield scrapy.Request(url=url,callback=self.parse)

	 def parseSongListInfo(self,response):
	 	#爬取歌单的基本信息
	 	songListInfo ={}
	 	songListInfo['name'] = response.xpath('//h2[@class="f-ff2 f-brk"]/text()').extract_first()
	 	songListInfo['createTime'] = response.xpath('//span[@class="time s-fc4"]/text()').extract_first()
	 	songListInfo['userId'] = response.xpath('//a[@class="face"]').xpath('@href').extract_first().split("=")[-1]
	 	songListInfo['songListId'] = response.url.split('=')[-1]
	 	songListInfo['songCount'] = response.xpath('//span[@id="playlist-track-count"]/text()').extract_first()
	 	songListInfo['playCount'] = response.xpath('//strong[@id="play-count"]/text()').extract_first()
	 	self.log(self.name+" : "+str(songListInfo))
	 	return songListInfo

	 def parseSongInfoList(self,response):
	 	songInfoList = []
	 	#temp = response.xpath('//table[@class="m-table "]/tbody/tr')
	 	#self.log(str(temp.extract()))
	 	#将songInfo放在外面，最后所有的songInfo都是最后一个？
	 	for songInfoTemp in response.xpath('.//table[@class="m-table "]/tbody/tr'):
	 		#self.log(songInfoTemp.extract())
	 		songInfo = {}
	 		songInfo['num'] = songInfoTemp.xpath('.//span[@class="num"]/text()').extract_first()
	 		songInfo['name'] = songInfoTemp.xpath('.//span[@class="txt"]/a/b').xpath('@title').extract_first()
	 		songInfo['href'] = songInfoTemp.xpath('.//span[@class="txt"]/a').xpath('@href').extract_first()
	 		songInfo['long'] = songInfoTemp.xpath('.//span[@class="u-dur "]/text()').extract_first()
	 		songInfo['singer'] = songInfoTemp.xpath('.//div[@class="text"]/span').xpath('@title').extract_first()
	 		songInfo['singerHref'] = songInfoTemp.xpath('.//div[@class="text"]/span/a').xpath('@href').extract_first()
	 		songInfo['album'] = songInfoTemp.xpath('.//div[@class="text"]/a').xpath('@title').extract_first()
	 		songInfo['albumHref'] = songInfoTemp.xpath('.//div[@class="text"]/a').xpath('@href').extract_first()
	 		songInfoList.append(songInfo)
	 	return songInfoList

	 def parse(self,response):
	 	driver = webdriver.Chrome()
	 	driver.get(response.url)
	 	wait = WebDriverWait(driver, 2)
	 	driver.switch_to_frame("contentFrame")
	 	response = response.replace(body=driver.page_source)
	 	file_name = 'SongListSpider_'+response.url.split('=')[-1]+'.txt'
	 	#爬取歌单的基本信息
	 	songListInfo = self.parseSongListInfo(response = response)
	 	#self.log(str(songListInfo))
	 	#爬取歌单中的歌曲信息
	 	songInfoList = self.parseSongInfoList(response = response)
	 	#汇总歌单信息并保存
	 	songListSpider = {'songListInfo':songListInfo,'songInfoList':songInfoList}
	 	f = codecs.open(file_name,'w','utf-8')
	 	f.write(json.dumps(songListSpider))
	 	f.close()
	 	self.log('Saved file %s ' % file_name)
