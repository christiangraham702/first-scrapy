import scrapy
from single_listing.items import ListCraigItem
from single_listing.stuff import good_links, headers
from single_listing.helpful_functions import get_base_url


class LinkFinderSpider(scrapy.Spider):
    name = 'link_finder'
    allowed_domains = ['craigslist.org']
    start_urls = ['http://craigslist.org/']

    filename = 'sun_test4'

    custom_settings = {
        'FEED_URI': f'data/{filename}.json',
        'FEED_FORMAT': 'json'
        # 'LOG_FILE': f'data/{filename}.log'
    }

    def parse(self, response):
        # good_links = [(link,zip)]
        for link in good_links:
            if link[1] == 'no zip code':
                continue
            search = f'/search/sss?query=baby+formula&search_distance=250&postal={link[1]}'
            url = link[0]+search
            yield scrapy.Request(url, callback=self.parse_page, headers=headers)

    def parse_page(self, response):
        loot = ListCraigItem()

        results = response.xpath(
            '//span[@class="button pagenum"]/text()').get()

        if not results:
            if results[:1] == 'no':
                loot['pid'] = 0
                loot['link'] = response.url
                yield loot
        else:
            num_items = response.xpath(
                '//span[@class="totalcount"]/text()').get()
            num_items = int(num_items)
            page_count = response.xpath(
                '//span[@class="rangeTo"]/text()').get()
            page_count = int(page_count)
            counter = 0
            new_page = False
            for pid in response.xpath('//li[@class="result-row"]/@data-pid').getall():
                if counter <= num_items:
                    loot['zip_code'] = response.xpath(
                        '//div[@class="searchgroup"]/input[@name="postal"]/@value').get()
                    loot['pid'] = float(pid)
                    loot['link'] = response.url
                    loot['title'] = response.xpath(
                        f'//li[@data-pid="{pid}"]//h3[@class="result-heading"]/a/text()').get()
                    loot['date'] = response.xpath(
                        f'//li[@data-pid="{pid}"]//time/@datetime').get()
                    loot['region'] = response.xpath(
                        f'//li[@data-pid="{pid}"]//span[@class="nearby"]/@title').get()
                    loot['dist_from_zip'] = response.xpath(
                        f'//li[@data-pid="{pid}"]//span[@class="maptag"]/text()').get()
                    if response.xpath(f'//li[@data-pid="{pid}"]//span[@class="result-price"]/text()').get():
                        loot['price'] = response.xpath(
                            f'//li[@data-pid="{pid}"]//span[@class="result-price"]/text()').get().replace('$', '').replace(',', '')
                    else:
                        loot['price'] = '-1'
                    counter += 1
                    yield loot
            if num_items > 120 and not page_count == num_items:
                next_page = response.xpath(
                    '//span[@class="buttons"]/a[@class="button next"]//@href').get()
                base_url = get_base_url(response.url)
                yield scrapy.Request(base_url+next_page, callback=self.parse_page, headers=headers)
