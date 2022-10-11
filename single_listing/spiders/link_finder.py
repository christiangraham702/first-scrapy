
import scrapy
from single_listing.items import ListCraigItem
from single_listing.stuff import good_links, headers
from single_listing.helpful_functions import get_base_url, get_num_listings, get_price, is_listings
from scrapy.loader import ItemLoader
from itemloaders.processors import MapCompose, TakeFirst

# this scraper follows all the links in single_listing.stuff, which covers the entire US.
# uses zip codes to make search radius 250 mi, allowing more items to be scraped with less requests
# because of increased search radius, lots of dupiclates from overlapping areas
# used a very simple algotrithim to acquire current set of links from all links in US
#   -- links were found by mapping ALL craigslist sites in US
#   -- then iterating through list of links and only including links 250mi away from previous link
#   -- definitely not the most optimal set of links but they work


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
        visited = 0
        for link in good_links:
            if visited > 10:
                break
            if link[1] == 'no zip code':
                continue
            search = f'/search/sss?query=baby+formula&search_distance=250&postal={link[1]}'
            url = link[0]+search
            visited += 1
            yield scrapy.Request(url, callback=self.parse_page, headers=headers)

    def parse_page(self, response):
        proc = TakeFirst()
        # checks for listings
        if is_listings(response):
            # pages to parse
            page_count = response.xpath(
                '//span[@class="rangeTo"]/text()').get()
            page_count = int(page_count)
            counter = 0
            # iterating through each pid and getting info for each one
            for pid in response.xpath('//li[@class="result-row"]/@data-pid').getall():
                l = ItemLoader(item=ListCraigItem(), response=response)
                # finds the number of items
                l.add_xpath(
                    'num_items', '//span[@class="totalcount"]/text()', MapCompose(get_num_listings))
                l.add_xpath(
                    'num_items', '//span[@class="button pagenum"]/text()', MapCompose(get_num_listings))
                num_items = l.get_output_value('num_items')
                num_items = int(num_items[0])
                if counter <= num_items:
                    l.add_xpath(
                        'zip_code', '//div[@class="searchgroup"]/input[@name="postal"]/@value', TakeFirst())
                    l.add_value('pid', float(pid))
                    l.add_value('link', response.url)
                    l.add_xpath(
                        'title', f'//li[@data-pid="{pid}"]//h3[@class="result-heading"]/a/text()', TakeFirst())
                    l.add_xpath(
                        'date', f'//li[@data-pid="{pid}"]//time/@datetime')
                    l.add_xpath(
                        'region', f'//li[@data-pid="{pid}"]//span[@class="nearby"]/@title')
                    l.add_xpath(
                        'dist_from_zip', f'//li[@data-pid="{pid}"]//span[@class="maptag"]/text()')
                    l.add_xpath(
                        'price', f'//li[@data-pid="{pid}"]//span[@class="result-price"]/text()', MapCompose(get_price))
                    l.replace_value('price', proc(l.get_output_value('price')))
                    counter += 1
                    yield l.load_item()
            # checking if need to go to next page
            if num_items > 120 and not page_count == num_items:
                next_page = response.xpath(
                    '//span[@class="buttons"]/a[@class="button next"]//@href').get()
                base_url = get_base_url(response.url)
                yield scrapy.Request(base_url+next_page, callback=self.parse_page, headers=headers)
