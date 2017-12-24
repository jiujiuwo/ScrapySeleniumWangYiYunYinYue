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
	name = 'TestSeleniumPageSpider'

	def start_requests(self):
		urls = ['https://music.163.com/song?id=102629','https://music.163.com/song?id=102629',]
		for url in urls:
			yield scrapy.Request(url = url,callback = self.parse)


	def parse(self,response):
		driver = webdriver.Chrome()
		driver.get(response.url)
		#wait = WebDriverWait(driver,2)

		element = WebDriverWait(driver, 2)

		driver.switch_to_frame("contentFrame")
		response = response.replace(body = driver.page_source)
		
		#通过浏览器点击翻页来爬取下一页的评论
		#首先获取动态的下一页的a标签的id
		nexPageId = response.xpath('//div[@class="m-cmmt"]/div/div/a').xpath("@id")[-1].extract()
		self.log(nexPageId)
		self.log(response.xpath('//div[@class="m-cmmt"]/div/div/a/text()')[-1].extract())
		btnNextPage = driver.find_element_by_id(nexPageId)
		self.log(btnNextPage)
		actions = webdriver.ActionChains(driver)
		self.log(btnNextPage)
		actions.move_to_element(btnNextPage)
		actions.click(btnNextPage)
		#如果没有线程的睡眠的话，会出错，经试验该值的最小值为3
		while(True):
			try:
				actions.perform()
				break;
			except:
				time.sleep(1)

		#汇总评论和歌曲的基本信息并保存




