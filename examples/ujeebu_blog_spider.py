"""
Ujeebu Blog Spider Example

This example demonstrates how to use UjeebuScrapeRequest with extract_rules
to scrape blog posts from https://ujeebu.com/blog

The extract_rules feature allows you to define extraction rules as JSON that
the Ujeebu API will use to extract structured data from the rendered page.

This spider extracts:
- Blog post titles
- Authors
- Excerpts
- Images
- Links to full articles
- Reading time estimates

Run with: scrapy runspider ujeebu_blog_spider.py -o blog_posts.json

Requirements:
- pip install scrapy ujeebu-scrapy
- Set your UJEEBU_API_KEY in the custom_settings below
"""
import os

import scrapy
from ujeebu_scrapy import UjeebuScrapeRequest


class UjeebuBlogSpider(scrapy.Spider):
    """
    Spider that extracts blog posts from ujeebu.com/blog using extract_rules.

    This demonstrates:
    - Using extract_rules for automatic structured data extraction
    - Extracting multiple items with nested data
    - POST request handling (extract_rules triggers POST mode)
    """

    name = 'ujeebu_blog'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),  # Replace with your API key
        'UJEEBU_DEFAULT_TIMEOUT': 60,
        # Recommended settings for API-based scraping
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'INFO',
    }

    # Extract rules for blog posts
    # This will be sent as POST body to the Ujeebu API
    extract_rules = {
        "blog_posts": {
            "selector": ".post-card",
            "type": "obj",
            "multiple": True,
            "children": {
                "title": {
                    "selector": ".post-card-title",
                    "type": "text"
                },
                "author": {
                    "selector": ".author-name-tooltip",
                    "type": "text"
                },
                "excerpt": {
                    "selector": ".post-card-excerpt p",
                    "type": "text"
                },
                "image": {
                    "selector": "img.post-card-image",
                    "type": "image"
                },
                "link": {
                    "selector": "a.post-card-content-link",
                    "type": "link"
                },
                "reading_time": {
                    "selector": ".reading-time",
                    "type": "text"
                }
            }
        }
    }

    def start_requests(self):
        """Generate the initial request to scrape the blog page."""

        self.logger.info("Starting to scrape Ujeebu blog...")

        yield UjeebuScrapeRequest(
            url='https://ujeebu.com/blog',
            extract_rules=self.extract_rules,
            # Enable JavaScript for dynamic content
            js=True,
            # Wait for content to load
            wait_for=2000,
            callback=self.parse_blog,
            errback=self.handle_error,
        )

    def parse_blog(self, response):
        """Parse the blog page response and yield blog post items."""

        self.logger.info(f"Received response from {response.url}")

        # The extract_rules results are in the JSON response
        # Parse the JSON response
        try:
            import json
            data = json.loads(response.text)

            # Check if extraction was successful
            if 'result' in data:
                extracted = data['result']
                blog_posts = extracted.get('blog_posts', [])

                self.logger.info(f"Found {len(blog_posts)} blog posts")

                for post in blog_posts:
                    yield {
                        'title': post.get('title', '').strip() if post.get('title') else None,
                        'author': post.get('author', '').strip() if post.get('author') else None,
                        'excerpt': post.get('excerpt', '').strip() if post.get('excerpt') else None,
                        'image': post.get('image'),
                        'link': post.get('link'),
                        'reading_time': post.get('reading_time', '').strip() if post.get('reading_time') else None,
                    }
            else:
                # If extract_rules format is different, try alternative parsing
                self.logger.warning("Unexpected response format, trying alternative parsing...")

                # Sometimes the extracted data is at a different path
                if 'extracted_data' in data:
                    blog_posts = data['extracted_data'].get('blog_posts', [])
                    for post in blog_posts:
                        yield {
                            'title': post.get('title', '').strip() if post.get('title') else None,
                            'author': post.get('author', '').strip() if post.get('author') else None,
                            'excerpt': post.get('excerpt', '').strip() if post.get('excerpt') else None,
                            'image': post.get('image'),
                            'link': post.get('link'),
                            'reading_time': post.get('reading_time', '').strip() if post.get('reading_time') else None,
                        }
                else:
                    self.logger.error(f"Could not find extracted data in response: {list(data.keys())}")

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Response text: {response.text[:500]}...")

    def handle_error(self, failure):
        """Handle request errors."""
        self.logger.error(f"Request failed: {failure.value}")


# Allow running directly with: python ujeebu_blog_spider.py
if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # Create a crawler process with settings
    process = CrawlerProcess({
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),  # Replace with your API key
        'UJEEBU_DEFAULT_TIMEOUT': 60,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'INFO',
        'FEEDS': {
            'blog_posts.json': {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 2,
            },
        },
    })

    process.crawl(UjeebuBlogSpider)
    process.start()

