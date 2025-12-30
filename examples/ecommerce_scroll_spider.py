"""
E-commerce Infinite Scroll Spider Example

A practical e-commerce crawler that handles infinite scroll product listings.

Run with: scrapy runspider ecommerce_scroll_spider.py -o ecommerce_products.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuScrapeRequest


class EcommerceCrawlerSpider(scrapy.Spider):
    """
    A practical e-commerce crawler that handles infinite scroll product listings.
    """

    name = 'ecommerce_scroll'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
    }

    def start_requests(self):
        """Start crawling product listings."""
        categories = [
            'https://books.toscrape.com',
            'https://books.toscrape.com/catalogue/page-2.html',
            'https://books.toscrape.com/catalogue/category/books/philosophy_7/index.html',
        ]

        for category_url in categories:
            yield UjeebuScrapeRequest(
                url=category_url,
                params={
                    'js': True,
                    'scroll_down': True,
                    'progressive_scroll': True,
                    'scroll_wait': 800,
                    'wait_for': '.product_pod',  # Wait for products to load
                },
                extract_rules={
                    "products": {
                        "children": {
                            "image": {
                                "selector": "div.image_container img",
                                "type": "image"
                            },
                            "name": {
                                "selector": "h3 a",
                                "type": "text"
                            },
                            "price": {
                                "selector": "p.price_color",
                                "type": "text"
                            },
                            "rating": {
                                "selector": "p.star-rating",
                                "type": "text"
                            },
                            "url": {
                                "selector": "h3 a",
                                "type": "link"
                            }
                        },
                        "multiple": True,
                        "selector": "article.product_pod",
                        "type": "obj"
                    }
                },
                callback=self.parse_products,
                meta={'category_url': category_url}
            )

    def parse_products(self, response):
        """Parse product listings."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse response for {response.url}")
            return

        if data.get('success'):
            result = data.get('result', {})

            products = result.get('products', [])

            for product in products:
                yield {
                    'category_url': response.meta.get('category_url'),
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'rating': product.get('rating'),
                    'image': product.get('image'),
                    'link': product.get('url'),
                }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(EcommerceCrawlerSpider)
    process.start()

