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

Run with: scrapy runspider proxy_spider.py -o geo_results.json
"""

import scrapy
from ujeebu_scrapy import UjeebuScrapeRequest, UjeebuSerpRequest


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

    name = 'proxy'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',  # Replace with your API key
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
                'json': True,
            },
            callback=self.parse_geo,
            meta={'proxy_type': 'rotating'}
        )

        # Example 2: Advanced proxy
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'advanced',
                'json': True,
            },
            callback=self.parse_geo,
            meta={'proxy_type': 'advanced'}
        )

        # Example 3: Premium proxy with geo-targeting
        countries = ['US', 'GB', 'DE', 'FR', 'JP', 'AU', 'BR', 'CA']

        for country in countries:
            yield UjeebuScrapeRequest(
                url=geo_check_url,
                params={
                    'proxy_type': 'premium',
                    'proxy_country': country,
                    'json': True,
                },
                callback=self.parse_geo,
                meta={'proxy_type': f'premium_{country}', 'target_country': country}
            )

        # Example 4: Residential proxy
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'residential',
                'proxy_country': 'US',
                'json': True,
            },
            callback=self.parse_geo,
            meta={'proxy_type': 'residential_US'}
        )

        # Example 5: Mobile proxy
        yield UjeebuScrapeRequest(
            url=geo_check_url,
            params={
                'proxy_type': 'mobile',
                'json': True,
            },
            callback=self.parse_geo,
            meta={'proxy_type': 'mobile'}
        )

        # Example 6: Session-based sticky proxy
        # All requests with same session_id use the same proxy IP
        session_id = 'mysession123'

        for i in range(3):
            yield UjeebuScrapeRequest(
                url=ip_check_url,
                params={
                    'proxy_type': 'premium',
                    'session_id': session_id,
                    'json': True,
                },
                callback=self.parse_ip,
                meta={'proxy_type': 'session', 'session_id': session_id, 'request_num': i + 1}
            )

        # Example 7: Auto-proxy (automatic fallback)
        yield UjeebuScrapeRequest(
            url='https://example-protected-site.com/',
            params={
                'auto_proxy': True,  # Automatically try better proxies if blocked
                'json': True,
            },
            callback=self.parse_page,
            meta={'proxy_type': 'auto'}
        )

        # Example 8: Custom proxy
        yield UjeebuScrapeRequest(
            url=ip_check_url,
            params={
                'proxy_type': 'custom',
                'custom_proxy': 'http://your-proxy-host:8080',
                'custom_proxy_username': 'your_username',
                'custom_proxy_password': 'your_password',
                'json': True,
            },
            callback=self.parse_ip,
            meta={'proxy_type': 'custom'}
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
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',
    }

    def start_requests(self):
        """Search in different locations."""
        search_query = 'best coffee shop'

        locations = [
            {'code': 'us', 'lang': 'en', 'name': 'United States'},
            {'code': 'gb', 'lang': 'en', 'name': 'United Kingdom'},
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
    process.crawl(ProxySpider)
    process.start()

