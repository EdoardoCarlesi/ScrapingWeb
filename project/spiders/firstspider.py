import scrapy


class FirstSpider(scrapy.Spider):

    name = "Books"
    start_url = [
            'https://books.toscrape.com/',
            'https://books.toscrape.com/catalogue/immunity-how-elie-metchnikoff-changed-the-course-of-modern-medicine_900/index.html'
            ]
        

    def parse(self, response):
        page = response.url.split('/')[-2]
        filename = 'books-%s.html' % page

        with open(filenanme, 'wb') as f:
            f.write(response.body)
