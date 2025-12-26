"""
Article Extractor Spider Example

This example demonstrates how to use UjeebuExtractRequest to extract
article content from news websites and blogs.

The Extract API automatically identifies and extracts:
- Article title, author, and publish date
- Main text and HTML content
- Featured image and embedded images
- Social media feeds and RSS links
- Article probability score

Run with: scrapy runspider article_extractor_spider.py -o articles.json
"""

import scrapy
from ujeebu_scrapy import UjeebuExtractRequest, UjeebuScrapeRequest


class ArticleExtractorSpider(scrapy.Spider):
    """
    A spider that extracts articles using the Ujeebu Extract API.

    This spider demonstrates:
    - Extracting article content from news sites
    - Using the Extract API with various options
    - Filtering articles based on is_article score
    - Combining Scrape and Extract APIs
    """

    name = 'article_extractor'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',  # Replace with your API key
    }

    def start_requests(self):
        """Generate article extraction requests."""

        # List of article URLs to extract
        article_urls = [
            'https://ujeebu.com/blog/integrating-ujeebus-web-scraper-api-with-rpa-for-scalable-web-data-extraction/',
            'https://ujeebu.com/blog/extracting-product-information-automatically-using-chatgpt/',
            'https://ujeebu.com/blog/building-a-crawler-with-scrapy/',
        ]

        for url in article_urls:
            # Example 1: Basic article extraction
            yield UjeebuExtractRequest(
                url=url,
                text=True,      # Extract text content
                html=True,      # Extract HTML content
                images=True,    # Extract images
                author=True,    # Extract author
                pub_date=True,  # Extract publish date
                is_article=True,  # Get article probability score
                callback=self.parse_article
            )

        # Example 2: Quick mode for faster extraction
        yield UjeebuExtractRequest(
            url='https://ujeebu.com/blog/building-a-crawler-with-scrapy/',
            quick_mode=True,  # Faster but less thorough
            text=True,
            callback=self.parse_article,
            meta={'mode': 'quick'}
        )

        # Example 3: Extract with JavaScript rendering
        yield UjeebuExtractRequest(
            url='https://ujeebu.com/blog/building-a-crawler-with-scrapy/',
            js=True,  # Enable JS rendering
            params={
                'js_timeout': 10,
                'wait_until': 'networkidle'
            },
            callback=self.parse_article,
            meta={'mode': 'js_rendered'}
        )

        # Example 4: Extract with media and feeds
        yield UjeebuExtractRequest(
            url='https://ujeebu.com/blog/building-a-crawler-with-scrapy/',
            media=True,   # Extract embedded media (YouTube, Twitter, etc.)
            feeds=True,   # Extract RSS feeds
            callback=self.parse_media_article
        )

    def parse_article(self, response):
        """Parse extracted article data."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON response from {response.url}")
            return

        # Check if extraction was successful
        if not data.get('success', True):
            self.logger.error(f"Extraction failed for {response.url}: {data.get('message')}")
            return

        # Extract article data from the 'article' field
        article = data.get('article', {})

        # Check article probability
        is_article = article.get('is_article', 0)
        if is_article < 0.5:
            self.logger.warning(f"Low article probability ({is_article}) for {response.url}")

        yield {
            'type': 'article',
            'url': response.url,
            'title': article.get('title'),
            'author': article.get('author'),
            'pub_date': article.get('pub_date'),
            'text': article.get('text'),
            'html': article.get('html'),
            'main_image': article.get('main_image'),
            'images': article.get('images', []),
            'is_article': is_article,
            'word_count': len(article.get('text', '').split()) if article.get('text') else 0,
            'mode': response.meta.get('mode', 'standard')
        }

    def parse_media_article(self, response):
        """Parse article with embedded media."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse JSON response from {response.url}")
            return

        # Extract article data from the 'article' field
        article = data.get('article', {})

        yield {
            'type': 'media_article',
            'url': response.url,
            'title': article.get('title'),
            'media': article.get('media', []),
            'feeds': article.get('feeds', []),
            'embeds': article.get('embeds', []),
        }


class NewsCrawlerSpider(scrapy.Spider):
    """
    A more comprehensive news crawler that combines Scrape and Extract APIs.

    This spider:
    1. Scrapes a news homepage to find article links
    2. Extracts full article content from each link
    """

    name = 'news_crawler'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',
    }

    def start_requests(self):
        """Start by scraping the news homepage."""
        yield UjeebuScrapeRequest(
            url='https://news.ycombinator.com/',
            js=False,  # HN doesn't need JS
            callback=self.parse_homepage
        )

    def parse_homepage(self, response):
        """Parse homepage and extract article links."""
        # Find all story links on Hacker News
        for story in response.css('.titleline'):
            link = story.css('a::attr(href)').get()
            title = story.css('a::text').get()

            if link and link.startswith('http'):
                # Extract article content using Extract API
                yield UjeebuExtractRequest(
                    url=link,
                    text=True,
                    html=True,
                    author=True,
                    pub_date=True,
                    is_article=True,
                    callback=self.parse_article,
                    meta={'hn_title': title}
                )

    def parse_article(self, response):
        """Parse extracted article."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return

        # Extract article data from the 'article' field
        article = data.get('article', {})

        if article.get('is_article', 0) >= 0.5:
            yield {
                'hn_title': response.meta.get('hn_title'),
                'url': response.url,
                'title': article.get('title'),
                'author': article.get('author'),
                'pub_date': article.get('pub_date'),
                'text_preview': article.get('text', '')[:500] + '...' if article.get('text') else None,
                'is_article': article.get('is_article'),
            }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(ArticleExtractorSpider)
    process.start()

