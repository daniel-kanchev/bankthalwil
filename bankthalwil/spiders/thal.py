import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bankthalwil.items import Article


class ThalSpider(scrapy.Spider):
    name = 'thal'
    start_urls = ['https://www.bankthalwil.ch/de/Magazin/Magazin/Aktuelles']

    def parse(self, response):
        links = response.xpath('//a[@class="more"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//span[@class="pagingPages"]/a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = datetime.strptime(date.strip(), '%d.%m.%Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="two-cols grid-offset-large-bottom"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
