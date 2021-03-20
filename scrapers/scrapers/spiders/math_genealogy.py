import re

import scrapy

class MathGenealogySpider(scrapy.Spider):
    name = "math_genealogy"

    start_urls = [
        'https://www.mathgenealogy.org/id.php?id=13'
    ]

    def parse(self, response):
        print('accessed page %s', response.url)
        page = re.search(r'id=(\d+)', response.url).group(1)
        print('page %s', page)
        with open(f'genealogy-{page}.html', 'wb') as f:
            f.write(response.body)
