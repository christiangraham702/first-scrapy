import scrapy
from single_listing.stuff import headers, helpful_stuff
from single_listing.items import CraigslistItem

# scrapy handles duplicate requests for u


class CraigslistSpider(scrapy.Spider):
    name = 'craigslist'
    allowed_domains = ['craigslist.org']
    start_urls = [
        'https://www.craigslist.org/about/sites']

    custom_settings = {
        'FEED_URI': 'data/kansas_full.json',
        'FEED_FORMAT': 'json',
    }

    def parse(self, response):
        state = 'Kansas'
        search = 'baby%20formula'
        # baby%20formula  -baby formula search
        query = f'/search/sss?query={search}'
        g_links = []
        for link in helpful_stuff[state]:
            g_links.append(link+query)
        for link in g_links:
            yield scrapy.Request(link, callback=self.parse_listings, headers=headers)

    # def check_listings(self, response):
    #     is_listings = response.css('span.button.pagenum::text').get()
    #     good_links = []
    #     if is_listings != 'no results':
    #         yield scrapy.Request(response.url, callback=self.parse_listings, headers=headers)

    def parse_listings(self, response):
        print('here******************')
        listings = response.css('li.result-row')
        b_urls = listings.css('a::attr(href)').getall()
        g_urls = b_urls[::3]
        for url in g_urls:
            yield scrapy.Request(url, callback=self.parse_item, headers=headers)

    def parse_item(self, response):
        item = CraigslistItem()

        item['description'] = response.xpath(
            '/html/head/meta[@property="og:description"]/@content').get()
        item['long'] = response.css('div::attr(data-longitude)').get()
        item['latitude'] = response.css('div::attr(data-latitude)').get()
        item['city'] = response.xpath(
            '/html/head/meta[@name="geo.placename"]/@content').get()
        item['region'] = response.xpath(
            '/html/head/meta[@name="geo.region"]/@content').get()
        item['price'] = response.css('span.price::text').get()
        item['posting_time'] = response.css('time::attr(datetime)').get()

        return item
