"""
Extract Rules Spider Example

This example demonstrates how to use UjeebuScrapeRequest with extract_rules
to scrape structured data from web pages without writing CSS selectors in Python.

The extract_rules feature allows you to define extraction rules as JSON that
the Ujeebu API will use to extract data from the rendered page.

Run with: scrapy runspider extract_rules_spider.py -o data.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuScrapeRequest


class ExtractRulesSpider(scrapy.Spider):
    """
    A spider that uses extract_rules for structured data extraction.

    This spider demonstrates:
    - Using extract_rules for automatic data extraction
    - Extracting multiple items with nested data
    - Different rule types (text, link, image, attr, obj)
    """

    name = 'extract_rules'

    # Define extract_rules as class attribute for reuse in pagination
    QUOTES_EXTRACT_RULES = {
        'quotes': {
            'selector': '.quote',
            'type': 'obj',
            'multiple': True,
            'children': {
                'text': {
                    'selector': '.text',
                    'type': 'text'
                },
                'author': {
                    'selector': '.author',
                    'type': 'text'
                },
                'author_link': {
                    'selector': 'a[href*="author"]',
                    'type': 'link'
                },
                'tags': {
                    'selector': '.tag',
                    'type': 'text',
                    'multiple': True
                }
            }
        },
        'next_page': {
            'selector': '.next a',
            'type': 'link'
        }
    }

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
    }

    def start_requests(self):
        """Generate requests with extract_rules."""

        # Example 1: Extract quotes with authors and tags
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/',
            extract_rules=self.QUOTES_EXTRACT_RULES,
            callback=self.parse_quotes,
            meta={'page': 1}
        )

        # Example 2: Extract product information
        yield UjeebuScrapeRequest(
            url='https://books.toscrape.com/',
            extract_rules={
                'products': {
                    'selector': 'article.product_pod',
                    'type': 'obj',
                    'multiple': True,
                    'children': {
                        'title': {
                            'selector': 'h3 a',
                            'type': 'attr',
                            'attribute': 'title'
                        },
                        'price': {
                            'selector': '.price_color',
                            'type': 'text'
                        },
                        'availability': {
                            'selector': '.availability',
                            'type': 'text'
                        },
                        'image': {
                            'selector': 'img',
                            'type': 'image'
                        },
                        'link': {
                            'selector': 'h3 a',
                            'type': 'link'
                        },
                        'rating': {
                            'selector': 'p.star-rating',
                            'type': 'attr',
                            'attribute': 'class'
                        }
                    }
                }
            },
            callback=self.parse_products
        )

        # Example 3: Extract meta information
        yield UjeebuScrapeRequest(
            url='https://ujeebu.com/blog',
            extract_rules={
                'title': {
                    'selector': 'title',
                    'type': 'text'
                },
                'meta_description': {
                    'selector': 'meta[name="description"]',
                    'type': 'attr',
                    'attribute': 'content'
                },
                'canonical_url': {
                    'selector': 'link[rel="canonical"]',
                    'type': 'attr',
                    'attribute': 'href'
                },
                'h1_text': {
                    'selector': 'h1',
                    'type': 'text'
                },
                'all_links': {
                    'selector': 'a',
                    'type': 'link',
                    'multiple': True
                }
            },
            callback=self.parse_meta
        )

    def parse_quotes(self, response):
        """Parse the extract_rules response for quotes."""
        import json

        # The response is JSON with the extracted data
        data = json.loads(response.text)

        if data.get('success'):
            result = data.get('result', {})

            # Yield each quote
            for quote in result.get('quotes', []):
                yield {
                    'type': 'quote',
                    'text': quote.get('text'),
                    'author': quote.get('author'),
                    'author_link': quote.get('author_link'),
                    'tags': quote.get('tags', []),
                    'page': response.meta.get('page', 1)
                }

            # Follow next page if available
            next_page = result.get('next_page')
            if next_page:
                yield UjeebuScrapeRequest(
                    url=response.urljoin(next_page),
                    extract_rules=self.QUOTES_EXTRACT_RULES,
                    callback=self.parse_quotes,
                    meta={'page': response.meta.get('page', 1) + 1}
                )
        else:
            self.logger.error(f"Extraction failed: {data.get('message')}")

    def parse_products(self, response):
        """Parse the extract_rules response for products."""
        import json

        data = json.loads(response.text)

        if data.get('success'):
            result = data.get('result', {})

            for product in result.get('products', []):
                # Extract rating from class (e.g., "star-rating Three")
                rating_class = product.get('rating', '')
                rating = rating_class.replace('star-rating ', '') if rating_class else None

                yield {
                    'type': 'product',
                    'title': product.get('title'),
                    'price': product.get('price'),
                    'availability': product.get('availability', '').strip(),
                    'image': product.get('image'),
                    'link': product.get('link'),
                    'rating': rating
                }

    def parse_meta(self, response):
        """Parse meta information from a page."""
        import json

        data = json.loads(response.text)

        if data.get('success'):
            yield {
                'type': 'meta',
                'url': response.url,
                **data.get('result', {})
            }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(ExtractRulesSpider)
    process.start()
