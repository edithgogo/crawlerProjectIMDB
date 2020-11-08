import os
from scrapy.selector import Selector

body = open('../../body.html').read()

x = Selector(text=body).xpath('//table[@class="chart full-width"]').get()

print(os.path.abspath(__file__))
