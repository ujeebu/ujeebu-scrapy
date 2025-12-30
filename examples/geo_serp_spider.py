"""
Geo-Targeted SERP Spider Example

This spider performs geo-targeted Google searches from different locations.

This is useful for:
- Local SEO analysis
- Competitor research in different markets
- Price comparison across regions

Run with: scrapy runspider geo_serp_spider.py -o geo_search_results.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuSerpRequest


class GeoTargetedSerpSpider(scrapy.Spider):
    """
    A spider that performs geo-targeted Google searches.

    This is useful for:
    - Local SEO analysis
    - Competitor research in different markets
    - Price comparison across regions
    """

    name = 'geo_serp'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
        'CONCURRENT_REQUESTS': 1,
    }

    def start_requests(self):
        """Search in different locations."""
        search_query = 'best coffee shop'

        locations = [
            {'code': 'us', 'lang': 'en', 'name': 'United States'},
            {'code': 'de', 'lang': 'de', 'name': 'Germany'},
            {'code': 'fr', 'lang': 'fr', 'name': 'France'},
            {'code': 'jp', 'lang': 'ja', 'name': 'Japan'},
        ]

        for loc in locations:
            yield UjeebuSerpRequest(
                search=search_query,
                search_type='search',
                location=loc['code'],
                lang=loc['lang'],
                results_count=10,
                callback=self.parse_results,
                meta={'location': loc['name'], 'query': search_query}
            )

    def parse_results(self, response):
        """Parse search results by location."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return

        location = response.meta.get('location')
        query = response.meta.get('query')

        # Yield summary
        yield {
            'type': 'geo_search_summary',
            'location': location,
            'query': query,
            'total_results': data.get('metadata', {}).get('number_of_results'),
        }

        # Yield individual results
        for result in data.get('organic_results', []):
            yield {
                'type': 'geo_search_result',
                'location': location,
                'query': query,
                'position': result.get('position'),
                'title': result.get('title'),
                'link': result.get('link'),
                'site_name': result.get('site_name'),
            }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(GeoTargetedSerpSpider)
    process.start()

