# -*-  coding: utf-8 -*-

import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import codecs
import json

class SongCommentListSpider(scrapy.Spider):
	name = 'SongCommentListSpider'

	def start_requests(self):
		urls = ['https://music.163.com/song?id=102629',]

		for url in urls:
			yield scrapy.Request(url = url,callback = self.parse)
	
	def parseSongInfo(self,response):
		songInfo = {}
		songInfo['name'] = response.xpath('//div[@class="tit"]/em/text()').extract_first()
		songInfo['songId'] = response.url.split("=")[-1]
		songInfo['singer'] = response.xpath('//div/p[@class="des s-fc4"]/span').xpath("@title").extract_first()
		songInfo['singerHref'] = response.xpath('//div/p[@class = "des s-fc4"]/span/a').xpath('@href').extract_first()
		songInfo['album'] = response.xpath('//div/p[@class="des s-fc4"]/a/text()').extract_first()
		songInfo['albumHref'] = response.xpath('//div/p[@class="des s-fc4"]/a').xpath('@href').extract_first()
		songInfo['commentsCount'] = response.xpath('//span[@class="sub s-fc3"]/span/text()').extract_first()
		self.log(str(songInfo))
		return songInfo

	def parseSongComments(self,response):
		commentList = []

		for commentTemp in response.xpath('//div[@class="cmmts j-flag"]/div'):
			commentInfo = {}

			tempUserId = commentTemp.xpath('.//div[@class="cnt f-brk"]/a').xpath('@href').extract_first()
			if tempUserId is not None:
				commentInfo['userId'] = tempUserId.split("=")[-1]

			commentInfo['userName'] = commentTemp.xpath('.//div[@class="cnt f-brk"]/a/text()').extract_first()
			commentInfo['content'] = commentTemp.xpath('.//div[@class="cnt f-brk"]/text()').extract_first()
			commentInfo['like'] = commentTemp.xpath('.//div[@class="rp"]/a/text()').extract_first()
			commentInfo['time'] = commentTemp.xpath('.//div[@class="time s-fc4"]/text()').extract_first()

			replyInfo = {}
			tempReply = commentTemp.xpath('.//div[@class="que f-brk f-pr s-fc3"]/a').xpath('@href').extract_first()
			if tempReply is not None:
				replyInfo['userId'] = tempReply.split("=")[-1]
				replyInfo['userName'] = commentTemp.xpath('.//div[@class="que f-brk f-pr s-fc3"]/a/text()').extract_first()
				replyInfo['content'] = commentTemp.xpath('.//div[@class="que f-brk f-pr s-fc3"]/text()').extract_first()
			commentInfo['replyTo'] = replyInfo
			self.log(str(commentInfo))
			commentList.append(commentInfo)
		return commentList

	def parse(self,response):
		driver = webdriver.Chrome()
		driver.get(response.url)
		wait = WebDriverWait(driver,2)

		driver.switch_to_frame("contentFrame")
		response = response.replace(body = driver.page_source)
		fileName = self.name+"_"+response.url.split('=')[-1]+".txt"

		#爬取歌曲的基本信息
		songInfo = self.parseSongInfo(response = response)
		#爬取评论信息
		commentInfoList = self.parseSongComments(response = response)
		#汇总歌曲和评论信息并保存
		songCommentListSpider = {'songInfo':songInfo,'commentInfoList':commentInfoList}
		f = codecs.open(fileName,'w','utf-8')
		f.write(json.dumps(songCommentListSpider))
		f.close()
		self.log('Saved file %s '% fileName)


		#汇总评论和歌曲的基本信息并保存




