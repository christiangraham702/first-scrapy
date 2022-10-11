
import scrapy
import csv
from single_listing.stuff import headers, helpful_stuff
from single_listing.items import ListCraigItem
from single_listing.helpful_functions import clean_pid_csv


class NewCraigSpider(scrapy.Spider):
    name = 'new_craig'
    allowed_domains = ['craigslist.org']
    start_urls = ['http://craigslist.org/']

    custom_settings = {
        'FEED_URI': 'data/florida_new4.json',
        'FEED_FORMAT': 'json',
    }

    def parse(self, response):
        state = 'Florida'
        search = 'baby%20formula'
        # baby%20formula  -baby formula search
        query = f'/search/sss?query={search}'
        g_links = []
        with open('data/less_pids2.csv', mode='r') as rf:
            pid_link = clean_pid_csv(rf)
            for link in pid_link:
                yield scrapy.Request(link, callback=self.parse_listings, headers=headers)

    def parse_listings(self, response):
        item2 = ListCraigItem()
        pids = []
        with open('data/less_pids2.csv', mode='r') as rf:
            pid_link = clean_pid_csv(rf)
            for pid in pid_link[response.url]:
                item2['title'] = response.xpath(
                    f'//li[@data-pid="{pid}"]//h3/a/text()').get()
                item2['date'] = response.xpath(
                    f'//li[@data-pid="{pid}"]//time/@datetime').get()
                item2['city'] = response.xpath(
                    f'//li[@data-pid="{pid}"]/span[@class="result-meta"]/span[@class="result-hood"]/text()').get()
                item2['price'] = response.xpath(
                    f'//li[@data-pid="{pid}"]/span[@class="result-meta"]/span[@class="result-price"]/text()').get()
                item2['link'] = response.xpath(
                    f'//li[@data-pid="{pid}"]/div[@class="result-info"]/h3[1]/a[@data-id="{pid}"]/@href').get()
                item2['pid'] = pid
        return item2
