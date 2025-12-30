"""
SERP and Scrape Combined Spider Example

This example demonstrates combining SERP and Scrape APIs to:
1. Search Google for relevant pages
2. Scrape the content from top results

Run with: scrapy runspider serp_and_scrape_spider.py -o combined_results.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuSerpRequest, UjeebuScrapeRequest


class SerpAndScrapeSpider(scrapy.Spider):
    """
    A spider that combines SERP and Scrape APIs to:
    1. Search Google for relevant pages
    2. Scrape the content from top results
    """

    name = 'serp_and_scrape'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
        'CONCURRENT_REQUESTS': 5,
    }

    def start_requests(self):
        """Search for pages to scrape."""
        yield UjeebuSerpRequest(
            search='python scrapy examples',
            search_type='search',
            results_count=5,
            callback=self.parse_serp
        )

    def parse_serp(self, response):
        """Parse SERP results and scrape each page."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return

        for result in data.get('organic_results', [])[:5]:
            link = result.get('link')
            if link:
                # Scrape each result page
                yield UjeebuScrapeRequest(
                    url=link,
                    js=True,
                    wait_for=2000,
                    callback=self.parse_page,
                    meta={
                        'serp_title': result.get('title'),
                        'serp_position': result.get('position'),
                    }
                )

    def parse_page(self, response):
        """Parse scraped page content."""
        yield {
            'url': response.url,
            'serp_title': response.meta.get('serp_title'),
            'serp_position': response.meta.get('serp_position'),
            'page_title': response.css('title::text').get(),
            'h1': response.css('h1::text').get(),
            'meta_description': response.css('meta[name="description"]::attr(content)').get(),
            'word_count': len(response.text.split()),
        }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(SerpAndScrapeSpider)
    process.start()

