import scrapy
from single_listing.stuff import headers, helpful_stuff
from single_listing.items import ListCraigItem


class ListingsCraigslistSpider(scrapy.Spider):
    name = 'listings_craigslist'
    allowed_domains = ['craigslist.org']
    start_urls = ['https://www.craigslist.org/about/sites']

    custom_settings = {
        'FEED_URI': 'data/kansas_by_listings2.json',
        'FEED_FORMAT': 'json',
    }

    def parse(self, response):
        state = 'California'
        search = 'baby%20formula'
        # baby%20formula  -baby formula search
        query = f'/search/sss?query={search}'
        g_links = []
        for link in helpful_stuff[state]:
            g_links.append(link+query)
        for link in g_links:
            yield scrapy.Request(link, callback=self.parse_listings, headers=headers)

    def parse_listings(self, response):
        if response.status == 200:
            num_items = response.xpath(
                '//span[@class="button pagenum"]/span[@class="totalcount"]/text()').get()
            if num_items:
                num_items = int(num_items)
                pids = response.xpath(
                    '//li[@class="result-row"]/@data-pid').getall()
                region = response.xpath(
                    '//ul[@class="breadcrumbs "]//option[1]/text()').get()
                dates = response.xpath(
                    '//li[@class="result-row"]/div[@class="result-info"]/time/@datetime').getall()
                # list of all prices, will be location if there is no price.
                prices = response.xpath(
                    '//li[@class="result-row"]/div[@class="result-info"]/span[2]/span[1]/text()').getall()
                titles = response.xpath(
                    '//li[@class="result-row"]/div[@class="result-info"]/h3[1]/a/text()').getall()
                for i in range(num_items):
                    item2 = ListCraigItem()
                    item2['title'] = titles[i]
                    item2['date'] = dates[i]
                    item2['region'] = region
                    # if cities != []:
                    #     item2['city'] = cities[i]
                    item2['link'] = response.url
                    item2['pid'] = pids[i]
                    if prices[i][:1] == '$':
                        item2['price'] = prices[i]
                    else:
                        item2['price'] = 'no price posted'

                    return item2
