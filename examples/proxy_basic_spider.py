"""
Proxy and Geo-Targeting Spider Example

This example demonstrates how to use different proxy types and
geo-targeting options with the Ujeebu Scrape API.

Proxy Types:
- rotating: Basic rotating proxies (default)
- advanced: More reliable rotating proxies
- premium: Premium proxies with country selection
- residential: Real residential IPs
- mobile: Mobile network IPs
- custom: Use your own proxy

Run with: scrapy runspider proxy_basic_spider.py -o geo_results.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuScrapeRequest


class ProxySpider(scrapy.Spider):
    """
    A spider demonstrating proxy and geo-targeting features.

    This spider demonstrates:
    - Different proxy types
    - Country-specific geo-targeting
    - Session-based sticky proxies
    - Using custom proxies
    - Auto-proxy fallback
    """

    name = 'proxy_basic'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
    }

    def start_requests(self):
        """Generate requests with different proxy configurations."""

        # URL that shows your IP and location
        ip_check_url = 'https://httpbin.org/ip'
        geo_check_url = 'https://ipinfo.io/json'

        # Example 1: Rotating proxy (default)
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'rotating',
            },
            response_type='raw',
            callback=self.parse_geo,
            meta={'proxy_type': 'rotating'}
        )

        # Example 2: Advanced proxy
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'advanced'
            },
            response_type='raw',
            callback=self.parse_geo,
            meta={'proxy_type': 'advanced'}
        )

        # Example 3: Premium proxy
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'premium',
                'proxy_country': 'US'
            },
            response_type='raw',
            callback=self.parse_geo,
            meta={'proxy_type': 'premium'}
        )

        # Example 4: residential proxy with geo-targeting
        countries = ['US', 'DE', 'FR', 'JP', 'AU', 'BR', 'CA']

        for country in countries:
            yield UjeebuScrapeRequest(
                url=geo_check_url,
                params={
                    'proxy_type': 'residential',
                    'proxy_country': country
                },
                response_type='raw',
                callback=self.parse_geo,
                dont_filter=True,
                meta={'proxy_type': f'residential_{country}', 'target_country': country}
            )

        # Example 6: Auto-proxy (automatic fallback)
        yield UjeebuScrapeRequest(
            url='https://books.toscrape.com/',
            params={
                'auto_proxy': True,  # Automatically try better proxies if blocked
            },
            response_type='raw',
            callback=self.parse_page,
            meta={'proxy_type': 'auto'}
        )

    def parse_geo(self, response):
        """Parse geo-location response."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse geo response")
            return

        yield {
            'type': 'geo_check',
            'proxy_type': response.meta.get('proxy_type'),
            'target_country': response.meta.get('target_country'),
            'actual_ip': data.get('ip'),
            'actual_country': data.get('country'),
            'city': data.get('city'),
            'region': data.get('region'),
            'org': data.get('org'),
        }

    def parse_ip(self, response):
        """Parse IP check response."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse IP response")
            return

        yield {
            'type': 'ip_check',
            'proxy_type': response.meta.get('proxy_type'),
            'session_id': response.meta.get('session_id'),
            'request_num': response.meta.get('request_num'),
            'ip': data.get('origin'),
        }

    def parse_page(self, response):
        """Parse generic page."""
        yield {
            'type': 'page',
            'proxy_type': response.meta.get('proxy_type'),
            'url': response.url,
            'status': response.status,
            'success': response.status == 200,
        }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(ProxySpider)
    process.start()

