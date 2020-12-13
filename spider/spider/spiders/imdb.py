import scrapy
from scrapy.selector import Selector
import os
import logging

def get_workspace_dir():
    return os.path.dirname(os.path.abspath(__file__))


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    couter = 0

    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES = {
            # fake user-agent, depend on the scrapy-user-agents package.
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        })


    def start_requests(self):
        urls = [
            'https://www.imdb.com/chart/top/?ref_=nv_mv_250',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)


    def parse(self, response):
        # increase the counter
        self.couter += 1
        if ImdbSpider.couter > 3:
            return

        print('url', response.url)
        page_name = response.url.split("/")[-2]

        file_path = os.path.join(get_workspace_dir(), 'data', page_name + ".html")

        with open(file_path, 'wb') as f:
            f.write(response.body)

        try:
            self.extract_fields(response)
        except:
            logging.error("error processing html")

        urls = response.xpath('//table[@class="chart full-width"]/tbody/tr/td[@class="titleColumn"]/a/@href').getall()

        for url in urls:
            next_url = response.urljoin(url)
            yield scrapy.Request(next_url, callback=self.parse)

    def extract_fields(self, response):
        '''
        Extract information from the response

        We are interested in the following informations:

        - Cast
        - Director
        - Storyline
        - Writer
        - Year
        - Title
        - RateVal
        - RateCount
        '''
        summary_root_xpath = '//div[@id="title-overview-widget"]/div/div/div[@class="credit_summary_item"]'
        items = response.xpath(summary_root_xpath)

        dic = {}
        for item in items:
            '''
            Get Writer, Director, Stars
            '''
            key = item.xpath("h4/text()").get()[:-1]
            value = item.xpath("a/text()").getall()
            dic[key] = value
            logging.info("extract {} : {}".format(key, value))

        # extract header
        dic["rating_value"] = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        dic["rating_count"] = response.xpath('//span[@itemprop="ratingCount"]/text()').get()
        dic["title"] = response.xpath('//div[@class="title_wrapper"]/h1/text()').get()
        dic["year"] = response.xpath('//div[@class="title_wrapper"]/h1/span[@id="titleYear"]/a/text()').get()

        print(dic)
