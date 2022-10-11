import scrapy
from single_listing.items import ListCraigPids
from single_listing.stuff import headers, helpful_stuff


class PidSnatcherSpider(scrapy.Spider):
    name = 'pid_snatcher'
    allowed_domains = ['craigslist.org']
    start_urls = ['http://craigslist.org/']

    filename = 'cali_num69'

    custom_settings = {
        'FEED_URI': f'data/{filename}.json',
        'FEED_FORMAT': 'json',
        'LOG_FILE': f'data/{filename}.log'
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
            yield scrapy.Request(link, callback=self.parse_pids, headers=headers)

    def parse_pids(self, response):
        pid_item = ListCraigPids()
        results = response.xpath(
            '//span[@class="button pagenum"]/text()').get()
        region = response.xpath(
            '//ul[@class="breadcrumbs "]//option[1]/text()').get()
        dates = response.xpath(
            '//li[@class="result-row"]/div[@class="result-info"]/time/@datetime').getall()
        # list of all prices, will be location if there is no price.
        prices = response.xpath(
            '//li[@class="result-row"]/div[@class="result-info"]/span[2]/span[1]/text()').getall()
        titles = response.xpath(
            '//li[@class="result-row"]/div[@class="result-info"]/h3[1]/a/text()').getall()
        if results[:2] == 'no':
            pid_item['pid'] = ' [no listings here]'
            pid_item['link'] = response.url
            yield pid_item
        else:
            num_items = response.xpath(
                '//span[@class="totalcount"]/text()').get()
            counter = 0
            for pid in response.xpath('//li[@class="result-row"]/@data-pid').getall():
                if counter < int(num_items):
                    pid_item['pid'] = pid
                    pid_item['link'] = response.url
                    pid_item['title'] = titles[counter]
                    pid_item['date'] = dates[counter]
                    pid_item['region'] = region
                    if prices[counter]:
                        if prices[counter][:1] == '$':
                            pid_item['price'] = prices[counter]
                        else:
                            pid_item['price'] = 'no price posted'
                    else:
                        pid_item['price'] = 'no price posted'
                    counter += 1
                else:
                    continue
                yield pid_item
