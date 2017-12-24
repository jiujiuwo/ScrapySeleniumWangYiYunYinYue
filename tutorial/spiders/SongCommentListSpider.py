# -*-  coding: utf-8 -*-

import scrapy
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import codecs
import json
import time

class SongCommentListSpider(scrapy.Spider):
	name = 'SongCommentListSpider'

	def start_requests(self):
		urls = ['http://music.163.com/song?id=16426485&userid=269241661','http://music.163.com/song?id=2175282','http://music.163.com/song?id=427606738']

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

	def parseSongCommentPage(self,response,driver):
		#首先获取动态的下一页的a标签的id
		nexPageId = response.xpath('//div[@class="m-cmmt"]/div/div/a').xpath("@id")[-1].extract()
		pageCount = response.xpath('//div[@class="m-cmmt"]/div/div/a/text()')[-2].extract()
		self.log("pageCount :"+str(pageCount))
		commentPageList = {}
		self.log(pageCount)
		time.sleep(3)
		for i in range(int(pageCount)-1):
			commentPage = {}
			btnNextPage = driver.find_element_by_id(nexPageId)
			actions = webdriver.ActionChains(driver)
			actions.move_to_element(btnNextPage)
			actions.click(btnNextPage)
			#如果没有线程的睡眠的话，会出错，经试验该值的最小值为3
			while(True):
				try:
					actions.perform()
					break;
				except:
					time.sleep(1)
			time.sleep(1)
			#调用第一页评论的爬取函数
			response = response.replace(body = driver.page_source)
			commentPageList[str(i+2)]= self.parseSongComments(response= response)
		return commentPageList

	def parse(self,response):
		driver = webdriver.Chrome()
		driver.get(response.url)
		wait = WebDriverWait(driver,2)

		driver.switch_to_frame("contentFrame")
		response = response.replace(body = driver.page_source)
		fileName = self.name+"_"+response.url.split('=')[-1]+".txt"

		#爬取歌曲的基本信息
		songInfo = self.parseSongInfo(response = response)

		commentPageList = {}
		#爬取第一页的评论信息
		firstPageComment = self.parseSongComments(response = response)

		commentPageList[str(1)] = firstPageComment
		
		#通过浏览器点击翻页来爬取下一页的评论
		commentPageList.update(self.parseSongCommentPage(response= response,driver = driver))

		#汇总歌曲和评论信息并保存
		songCommentListSpider = {'songInfo':songInfo,'commentPageList':commentPageList}
		f = codecs.open(fileName,'w','utf-8')
		f.write(json.dumps(songCommentListSpider))
		f.close()
		self.log('Saved file %s '% fileName)


		#汇总评论和歌曲的基本信息并保存




