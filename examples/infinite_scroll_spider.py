"""
Infinite Scroll Spider Example

This example demonstrates how to use UjeebuScrapeRequest to handle
pages with infinite scroll or lazy-loaded content.

The Ujeebu Scrape API provides several scrolling options:
- scroll_down: Enable scrolling
- scroll_wait: Wait time between scrolls
- progressive_scroll: Scroll until content stops loading
- scroll_callback: Custom JS to control scrolling
- scroll_to_selector: Scroll to specific element

Run with: scrapy runspider infinite_scroll_spider.py -o products.json
"""

import scrapy
from ujeebu_scrapy import UjeebuScrapeRequest


class InfiniteScrollSpider(scrapy.Spider):
    """
    A spider that handles infinite scroll pages.

    This spider demonstrates:
    - Basic scrolling to load more content
    - Progressive scrolling until no more content
    - Scroll callbacks for custom logic
    - Combining scrolling with extract_rules
    """

    name = 'infinite_scroll'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',  # Replace with your API key
    }

    def start_requests(self):
        """Generate requests for infinite scroll pages."""

        # Example 1: Basic scroll to end of page
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/scroll',
            params={
                'js': True,
                'scroll_down': True,
                'scroll_wait': 500,  # Wait 500ms between scrolls
            },
            callback=self.parse_quotes,
            meta={'scroll_type': 'basic'}
        )

        # Example 2: Progressive scroll (keeps scrolling until content stops loading)
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/scroll',
            params={
                'js': True,
                'scroll_down': True,
                'progressive_scroll': True,  # Keep scrolling until page height doesn't change
                'scroll_wait': 1000,
            },
            callback=self.parse_quotes,
            meta={'scroll_type': 'progressive'}
        )

        # Example 3: Scroll with extract_rules
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/scroll',
            params={
                'js': True,
                'scroll_down': True,
                'progressive_scroll': True,
                'scroll_wait': 500,
            },
            extract_rules={
                'quotes': {
                    'selector': '.quote',
                    'type': 'obj',
                    'multiple': True,
                    'children': {
                        'text': {'selector': '.text', 'type': 'text'},
                        'author': {'selector': '.author', 'type': 'text'},
                        'tags': {'selector': '.tag', 'type': 'text', 'multiple': True}
                    }
                }
            },
            callback=self.parse_extracted_quotes,
            meta={'scroll_type': 'with_extract_rules'}
        )

        # Example 4: Scroll to specific element
        yield UjeebuScrapeRequest(
            url='https://example-long-page.com/',
            params={
                'js': True,
                'scroll_down': True,
                'scroll_to_selector': '#footer',  # Scroll until footer is visible
            },
            callback=self.parse_page,
            meta={'scroll_type': 'to_selector'}
        )

        # Example 5: Custom scroll callback (advanced)
        # The callback should return true to continue scrolling, false to stop
        scroll_callback_js = '''
        () => {
            // Stop scrolling after 10 quotes are loaded
            const quotes = document.querySelectorAll('.quote');
            return quotes.length < 10;
        }
        '''

        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/scroll',
            params={
                'js': True,
                'scroll_down': True,
                'scroll_callback': scroll_callback_js,
                'scroll_wait': 500,
            },
            callback=self.parse_quotes,
            meta={'scroll_type': 'callback_limited'}
        )

        # Example 6: Click "Load More" button with custom JS + scroll
        load_more_js = '''
        async () => {
            const button = document.querySelector('.load-more-btn');
            if (button) {
                for (let i = 0; i < 5; i++) {
                    button.click();
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
        }
        '''

        yield UjeebuScrapeRequest(
            url='https://example-loadmore.com/',
            params={
                'js': True,
                'custom_js': load_more_js,
                'wait_for': 6000,  # Wait for all clicks to process
            },
            callback=self.parse_page,
            meta={'scroll_type': 'load_more_button'}
        )

    def parse_quotes(self, response):
        """Parse quotes from scrolled page."""
        scroll_type = response.meta.get('scroll_type')

        quotes = []
        for quote in response.css('.quote'):
            quotes.append({
                'text': quote.css('.text::text').get(),
                'author': quote.css('.author::text').get(),
                'tags': quote.css('.tag::text').getall(),
            })

        yield {
            'scroll_type': scroll_type,
            'url': response.url,
            'total_quotes': len(quotes),
            'quotes': quotes,
        }

    def parse_extracted_quotes(self, response):
        """Parse quotes extracted using extract_rules."""
        import json

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to parse JSON response")
            return

        if data.get('success'):
            result = data.get('result', {})
            quotes = result.get('quotes', [])

            yield {
                'scroll_type': response.meta.get('scroll_type'),
                'url': response.url,
                'total_quotes': len(quotes),
                'quotes': quotes,
            }

    def parse_page(self, response):
        """Generic page parser."""
        yield {
            'scroll_type': response.meta.get('scroll_type'),
            'url': response.url,
            'title': response.css('title::text').get(),
            'body_length': len(response.text),
        }


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
        'UJEEBU_API_KEY': '__YOUR_API_KEY__',
    }

    def start_requests(self):
        """Start crawling product listings."""
        categories = [
            'https://example-shop.com/electronics',
            'https://example-shop.com/clothing',
            'https://example-shop.com/books',
        ]

        for category_url in categories:
            yield UjeebuScrapeRequest(
                url=category_url,
                params={
                    'js': True,
                    'scroll_down': True,
                    'progressive_scroll': True,
                    'scroll_wait': 800,
                    'wait_for': '.product-card',  # Wait for products to load
                },
                extract_rules={
                    'products': {
                        'selector': '.product-card',
                        'type': 'obj',
                        'multiple': True,
                        'children': {
                            'name': {'selector': '.product-name', 'type': 'text'},
                            'price': {'selector': '.price', 'type': 'text'},
                            'original_price': {'selector': '.original-price', 'type': 'text'},
                            'rating': {'selector': '.rating', 'type': 'text'},
                            'reviews': {'selector': '.reviews-count', 'type': 'text'},
                            'image': {'selector': 'img', 'type': 'image'},
                            'link': {'selector': 'a', 'type': 'link'},
                        }
                    },
                    'category_name': {'selector': 'h1', 'type': 'text'},
                    'total_products': {'selector': '.product-count', 'type': 'text'},
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

            category_name = result.get('category_name', 'Unknown')
            products = result.get('products', [])

            for product in products:
                yield {
                    'category': category_name,
                    'category_url': response.meta.get('category_url'),
                    'name': product.get('name'),
                    'price': product.get('price'),
                    'original_price': product.get('original_price'),
                    'rating': product.get('rating'),
                    'reviews': product.get('reviews'),
                    'image': product.get('image'),
                    'link': product.get('link'),
                }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(InfiniteScrollSpider)
    process.start()

