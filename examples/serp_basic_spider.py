"""
SERP (Search Engine Results Page) Spider Example

This example demonstrates how to use UjeebuSerpRequest to get
search results from Google programmatically.

The SERP API supports:
- Web search, Images, News, Videos, and Maps
- Location and language targeting
- Device emulation (desktop, mobile, tablet)
- Pagination

Run with: scrapy runspider serp_basic_spider.py -o search_results.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuSerpRequest


class SerpSpider(scrapy.Spider):
    """
    A spider that searches Google using the Ujeebu SERP API.

    This spider demonstrates:
    - Web search with various parameters
    - Different search types (news, images, videos)
    - Location and language targeting
    - Pagination through results
    """

    name = 'serp_basic'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
    }

    def start_requests(self):
        """Generate SERP requests."""

        # Example 1: Basic web search
        yield UjeebuSerpRequest(
            search='python web scraping tutorial',
            search_type='search',
            lang='en',
            location='us',
            results_count=10,
            callback=self.parse_web_results,
            meta={'query_type': 'web'}
        )

        # Example 2: News search
        yield UjeebuSerpRequest(
            search='artificial intelligence news',
            search_type='news',
            lang='en',
            location='us',
            callback=self.parse_news_results,
            meta={'query_type': 'news'}
        )

        # Example 3: Image search
        yield UjeebuSerpRequest(
            search='python programming logo',
            search_type='images',
            results_count=20,
            callback=self.parse_image_results,
            meta={'query_type': 'images'}
        )

        # Example 4: Video search
        yield UjeebuSerpRequest(
            search='scrapy tutorial',
            search_type='videos',
            callback=self.parse_video_results,
            meta={'query_type': 'videos'}
        )

        # Example 5: Location-specific search
        yield UjeebuSerpRequest(
            search='best restaurants',
            search_type='search',
            lang='fr',
            location='fr',  # France
            device='mobile',  # Mobile search results
            callback=self.parse_web_results,
            meta={'query_type': 'local_mobile'}
        )

        # Example 6: Paginated search
        for page in range(1, 4):  # Get first 3 pages
            yield UjeebuSerpRequest(
                search='machine learning',
                search_type='search',
                page=page,
                results_count=10,
                callback=self.parse_web_results,
                meta={'query_type': 'paginated', 'page': page}
            )

    def parse_web_results(self, response):
        """Parse web search results."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse SERP response")
            return

        # Extract metadata
        metadata = data.get('metadata', {})
        yield {
            'type': 'search_metadata',
            'query_type': response.meta.get('query_type'),
            'page': response.meta.get('page', 1),
            'query_displayed': metadata.get('query_displayed'),
            'number_of_results': metadata.get('number_of_results'),
            'results_time': metadata.get('results_time'),
        }

        # Extract organic results
        for result in data.get('organic_results', []):
            yield {
                'type': 'organic_result',
                'query_type': response.meta.get('query_type'),
                'position': result.get('position'),
                'title': result.get('title'),
                'link': result.get('link'),
                'site_name': result.get('site_name'),
                'description': result.get('description'),
                'cite': result.get('cite'),
            }

        # Extract knowledge graph if present
        kg = data.get('knowledge_graph')
        if kg:
            yield {
                'type': 'knowledge_graph',
                'title': kg.get('title'),
                'description': kg.get('description'),
                **{k: v for k, v in kg.items() if k not in ['title', 'description']}
            }

        # Extract related questions
        for question in data.get('related_questions', []):
            yield {
                'type': 'related_question',
                'question': question,
            }

    def parse_news_results(self, response):
        """Parse news search results."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse news SERP response")
            return

        for result in data.get('news_results', data.get('organic_results', [])):
            yield {
                'type': 'news_result',
                'title': result.get('title'),
                'link': result.get('link'),
                'source': result.get('source') or result.get('site_name'),
                'date': result.get('date'),
                'snippet': result.get('snippet') or result.get('description'),
            }

    def parse_image_results(self, response):
        """Parse image search results."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse image SERP response")
            return

        for result in data.get('image_results', []):
            yield {
                'type': 'image_result',
                'title': result.get('title'),
                'link': result.get('link'),
                'thumbnail': result.get('thumbnail'),
                'source': result.get('source'),
            }

    def parse_video_results(self, response):
        """Parse video search results."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse video SERP response")
            return

        for result in data.get('video_results', data.get('videos', [])):
            yield {
                'type': 'video_result',
                'title': result.get('title'),
                'link': result.get('link'),
                'author': result.get('author'),
                'date': result.get('date'),
                'duration': result.get('duration'),
            }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(SerpSpider)
    process.start()

