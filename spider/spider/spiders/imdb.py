import scrapy
from scrapy.selector import Selector
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
import os
import logging
from ..items import ImdbItem

logging.getLogger('scrapy').setLevel(logging.WARNING)


def get_workspace_dir():
    return os.path.dirname(os.path.abspath(__file__))


class ImdbSpider(scrapy.Spider):
    name = "imdb"
    couter = 0
    allowed_domains = ['imdb.com']


    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES = {
            # fake user-agent, depend on the scrapy-user-agents package.
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
        ITEM_PIPELINES = {
            'spider.pipelines.SpiderPipeline': 300,
            'spider.pipelines.ImdbPipeline': 400
        }
    )

    rules = (Rule(
        LinkExtractor(restrict_css=('div.desc a')),
        follow=True,
        callback='parse_top_page',
    ),)


    def start_requests(self):
        urls = [
            'https://www.imdb.com/chart/top/?ref_=nv_mv_250',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_top_page)

    def parse_top_page(self, response):
        # increase the counter
        self.couter += 1
        if ImdbSpider.couter > 3:
            return

        page_name = response.url.split("/")[-2]

        file_path = os.path.join(get_workspace_dir(), 'data', page_name + ".html")

        with open(file_path, 'wb') as f:
            f.write(response.body)

        # self.extract_fields(response)

        urls = response.xpath('//table[@class="chart full-width"]/tbody/tr/td[@class="titleColumn"]/a/@href').getall()

        for url in urls:
            next_url = response.urljoin(url)
            yield response.follow(next_url, callback=self.parse_movie_page)


    def parse_movie_page(self, response):
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

        record = ImdbItem()
        for item in items:
            '''
            Get Writer, Director, Stars
            '''
            key = item.xpath("h4/text()").get()[:-1]
            value = item.xpath("a/text()").getall()
            logging.info("extract {} : {}".format(key, value))

            if key == "Writers": record['writer'] = value
            elif key == "Director": record['director'] = value
            elif key == "Stars": record['stars'] = value

        # extract header
        record['rating_value'] = response.xpath('//span[@itemprop="ratingValue"]/text()').get()
        record['rating_count'] = response.xpath('//span[@itemprop="ratingCount"]/text()').get()
        record['title'] = response.xpath('//div[@class="title_wrapper"]/h1/text()').get()
        record['year'] = response.xpath('//div[@class="title_wrapper"]/h1/span[@id="titleYear"]/a/text()').get()

        yield record
