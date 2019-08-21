import requests
from lxml import etree
import pymysql
import time


class Html_Spider:
	def __init__(self):
		self.url = 'https://www.html.cn/archives/category/xhtmlcss/page/{}'
		self.headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
		}
		# 链接数据库
		self.conn= pymysql.connect(host= 'localhost', port= 3306, user= 'root', password= '123456', database= 'jd', charset= 'utf8')
		self.cursor = self.conn.cursor()

	# 获取url
	def get_url(self, url):
		return [url.format(item) for item in range(1, 34)]

	#获取html
	def get_html(self, url):
		res = requests.get(url= url, headers= self.headers)
		return res.content.decode()

	#解析html
	def parse_html(self, html_str):
		html = etree.HTML(html_str)
		article = html.xpath("//div[@class='content']/article")
		html_list = []
		for item in article:
			pic = f'html.cn{item.xpath("./a/img/@data-src")[0]}' if len(item.xpath("./a/img/@data-src"))>0 else None
			link = f'html.cn{item.xpath("./header/h2/a/@href")[0]}' if len(item.xpath("./header/h2/a/@href"))>0 else None
			title = item.xpath('./header/h2/a/text()')[0] if len(item.xpath('./header/h2/a/text()'))>0 else None 
			note = item.xpath("./p[@class='note']/text()")[0] if len(item.xpath("./p[@class='note']/text()"))>0 else None
			html_list.append({
				"pic": pic,
				"link": link,
				"title": title,
				"note": note
				})
		return html_list

	#保存数据到数据库
	def save_data(self, data):
		sql = "insert into html(pic, link, title, note) values (%s, %s, %s, %s)"
		item = [data['pic'], data['link'], data['title'], data['link']]
		self.cursor.execute(sql, [*item])
		self.conn.commit()


	def run(self):
		# 获取url列表
		url_list= self.get_url(self.url)

		# 获取html
		html_str_list= []
		for item in url_list:
			start = time.time()
			html_str_list.append(self.get_html(item))
			end = time.time()
			print(f'获取第{url_list.index(item)+1}页: 耗时 {end-start} 秒')

		# 解析html
		data_list=[]
		for item in html_str_list:
			data_list.append(self.parse_html(item))

		# 保存数据
		for item in data_list:
			for sub in item:
				self.save_data(sub)

	#关闭数据库
	def __del__(self):
		self.cursor.close()
		self.conn.close()
		

if __name__ == '__main__':
	html = Html_Spider()
	html.run()