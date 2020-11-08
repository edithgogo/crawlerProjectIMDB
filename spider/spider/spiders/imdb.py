import scrapy
from scrapy.selector import Selector
import os

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
        if ImdbSpider.couter > 10:
            return

        print('url', response.url)
        page_name = response.url.split("/")[-2]

        file_path = os.path.join(get_workspace_dir(), 'data', page_name + ".html")

        with open(file_path, 'wb') as f:
            f.write(response.body)

        urls = response.xpath('//table[@class="chart full-width"]/tbody/tr/td[@class="titleColumn"]/a/@href').getall()

        for url in urls:
            next_url = response.urljoin(url)
            yield scrapy.Request(next_url, callback=self.parse)
