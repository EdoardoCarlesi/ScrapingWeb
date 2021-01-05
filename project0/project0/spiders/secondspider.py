import scrapy
from project0.items import Project0Item
    
class SecondSpider(scrapy.Spider):

    name = "Books2"
    start_url = [
            'https://books.toscrape.com/catalogue/immunity-how-elie-metchnikoff-changed-the-course-of-modern-medicine_900/index.html'
            ]
        

    def parse(self, response):
        item = Project0Item()
        item['title'] = response.xpath()
        item['price'] = response.xpath()
