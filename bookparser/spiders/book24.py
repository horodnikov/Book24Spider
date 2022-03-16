import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class Book24Spider(scrapy.Spider):
    mark = 'Борис Акунин'
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = [f'https://book24.ru/search/?q={mark}']

    def parse(self, response: HtmlResponse):
        books_links = response.xpath(
            "//div[contains(@class, 'product-card__content')]/a/@href").getall()
        for link in books_links:
            yield response.follow(link, callback=self.parse_books)
        next_page = response.xpath(
            "//a[contains(@class,'next smartLink')]/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_books(self, response: HtmlResponse):
        domain = self.allowed_domains
        link = response.url
        title = response.xpath(
            "//div[contains(@class, 'product-characteristic product-detail')]"
            "//li[position() = 2]//a/text()").get()
        authors = response.xpath(
            "//div[contains(@class, 'product-characteristic product-detail')]"
            "//li[position() = 1]//a/text()").get()
        rating = response.xpath(
            "//div[contains(@class, 'rating-widget')]"
            "//span[position() = 2]/text()").get()
        price_old = response.xpath(
            "//span[contains(@class, 'price-old')]/text()").get()
        price_actual = response.xpath(
            "//div[contains(@itemprop, 'offers')]//span[contains(@class, "
            "'app-price product-sidebar-price__price')]/text()").get()
        yield BookparserItem(
            domain=domain, link=link, title=title, authors=authors,
            rating=rating, price_old=price_old, price_actual=price_actual)
