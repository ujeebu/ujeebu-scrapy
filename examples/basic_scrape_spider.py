"""
Basic Scrape Spider Example

This example demonstrates how to use UjeebuScrapeRequest to scrape a
JavaScript-rendered page with the Ujeebu Scrape API.

Run with: scrapy runspider basic_scrape_spider.py -o output.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuScrapeRequest


class BasicScrapeSpider(scrapy.Spider):
    """
    A basic spider that scrapes a page using Ujeebu Scrape API.

    This spider demonstrates:
    - JavaScript rendering with wait conditions
    - Custom proxy settings
    - Parsing the rendered HTML response
    """

    name = 'basic_scrape'

    custom_settings = {
        # Enable Ujeebu middleware
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        # Ujeebu API configuration
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
        # Optional: Set default proxy type for all requests
        # 'UJEEBU_DEFAULT_PROXY_TYPE': 'rotating',
        'CONCURRENT_REQUESTS': 10,
        'CLOSESPIDER_TIMEOUT': 180,
        'DEPTH_LIMIT': 2
    }

    def start_requests(self):
        """Generate initial requests."""

        # Example 1: Basic request with JavaScript rendering
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/js/',
            params={
                'js': True,
                'wait_for': 2000,  # Wait 2 seconds for JS to render
            },
            callback=self.parse_quotes
        )

        # Example 2: Using named parameters (cleaner syntax)
        yield UjeebuScrapeRequest(
            url='https://httpbin.org/headers',
            js=True,
            response_type='raw',
            proxy_type='rotating',
            callback=self.parse_headers,
            meta={'example': 'named_params'}
        )

        # Example 3: Wait for specific element
        yield UjeebuScrapeRequest(
            url='https://books.toscrape.com/',
            params={
                'js': True,
                'wait_for': '.page_inner',  # Wait for element with class 'quote'
            },
            callback=self.parse_quotes,
            meta={'example': 'wait_for_selector'}
        )

    def parse_quotes(self, response):
        """Parse quotes from the page."""
        for quote in response.css('.quote'):
            yield {
                'text': quote.css('.text::text').get(),
                'author': quote.css('.author::text').get(),
                'tags': quote.css('.tag::text').getall(),
            }

    def parse_headers(self, response):
        """Parse headers response from httpbin."""
        import json
        data = json.loads(response.text)
        yield {
            'headers': data.get('headers', {}),
            'user_agent': data.get('headers', {}).get('User-Agent'),
        }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'DEBUG',
    })
    process.crawl(BasicScrapeSpider)
    process.start()
