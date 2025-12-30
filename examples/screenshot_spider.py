"""
Screenshot and PDF Spider Example

This example demonstrates how to use UjeebuScrapeRequest to
capture screenshots and generate PDFs of web pages.

IMPORTANT: About dont_filter=True
-------------------------------------
This spider uses dont_filter=True for testing purposes because we're making
multiple requests to the SAME URLs with DIFFERENT Ujeebu parameters.

By default, Scrapy filters duplicate requests based on the URL to avoid
re-scraping the same page. However, in this example, we want to:
- Capture fullpage vs viewport screenshots of the same URL
- Generate both screenshots AND PDFs of the same URL
- Test different device types (mobile, desktop) for the same URL
- Capture specific elements vs full pages

Since the target URLs are the same but the Ujeebu parameters (response_type,
screenshot_fullpage, device, etc.) are different, we use dont_filter=True
to tell Scrapy: "Yes, I know this URL was already requested, but this is a
different operation with different parameters - please process it anyway."

In production, you typically wouldn't need dont_filter=True unless you're
intentionally scraping the same URL with different configurations.

Run with: scrapy runspider screenshot_spider.py
"""

import base64
import json
import os
from datetime import datetime

import scrapy
from ujeebu_scrapy import UjeebuScrapeRequest


class ScreenshotSpider(scrapy.Spider):
    """
    A spider that captures screenshots and PDFs using the Ujeebu Scrape API.

    This spider demonstrates:
    - Full page screenshots
    - Viewport-only screenshots
    - Partial/element screenshots
    - PDF generation
    - Mobile device screenshots
    """

    name = 'screenshots'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
    }

    # Output directory for saved files
    OUTPUT_DIR = 'screenshots_output'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Create output directory
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def start_requests(self):
        """Generate screenshot and PDF requests."""

        urls = [
            'https://ujeebu.com/blog/',
            'https://quotes.toscrape.com/',
            'https://httpbin.org/html',
        ]

        for url in urls:
            # Example 1: Full page screenshot
            # Note: dont_filter=True allows multiple requests to same URL with different params
            yield UjeebuScrapeRequest(
                url=url,
                params={
                    'response_type': 'screenshot',
                    'screenshot_fullpage': True,
                    'js': True,
                    'wait_for': 1000,
                    'json': True,  # Get base64-encoded response
                },
                callback=self.save_screenshot,
                dont_filter=True,  # Allow this request even if URL was already requested
                meta={'screenshot_type': 'fullpage'}
            )

            # Example 2: Viewport screenshot (what user sees)
            # Note: Same URL as above but different screenshot_fullpage parameter
            yield UjeebuScrapeRequest(
                url=url,
                params={
                    'response_type': 'screenshot',
                    'screenshot_fullpage': False,
                    'js': True,
                    'json': True,
                },
                callback=self.save_screenshot,
                dont_filter=True,  # Different params (viewport vs fullpage) = different operation
                meta={'screenshot_type': 'viewport'}
            )

            # Example 3: PDF generation
            # Note: Same URL but different response_type (pdf vs screenshot)
            yield UjeebuScrapeRequest(
                url=url,
                params={
                    'response_type': 'pdf',
                    'js': True,
                    'wait_for': 1000,
                    'json': True,
                },
                dont_filter=True,  # Different response_type = different operation
                callback=self.save_pdf,
                meta={'doc_type': 'pdf'}
            )

        # Example 4: Mobile screenshot
        # Note: Same URL but different device type
        yield UjeebuScrapeRequest(
            url='https://ujeebu.com/blog/',
            params={
                'response_type': 'screenshot',
                'device': 'iPhone 12',
                'screenshot_fullpage': True,
                'js': True,
                'json': True,
            },
            dont_filter=True,  # Different device = different screenshot
            callback=self.save_screenshot,
            meta={'screenshot_type': 'mobile_iphone12'}
        )

        # Example 5: Custom viewport size
        # Note: Same URL but custom dimensions
        yield UjeebuScrapeRequest(
            url='https://ujeebu.com/blog/',
            params={
                'response_type': 'screenshot',
                'window_width': 1920,
                'window_height': 1080,
                'screenshot_fullpage': False,
                'js': True,
                'json': True,
            },
            dont_filter=True,  # Different viewport dimensions = different screenshot
            callback=self.save_screenshot,
            meta={'screenshot_type': 'custom_1920x1080'}
        )

        # Example 6: Partial screenshot (specific element)
        # Note: Capturing only a specific element, not the full page
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/',
            params={
                'response_type': 'screenshot',
                'screenshot_partial': '.quote:first-child',  # CSS selector
                'js': True,
                'json': True,
            },
            dont_filter=True,  # Different screenshot_partial = different screenshot
            callback=self.save_screenshot,
            meta={'screenshot_type': 'element_quote'}
        )

        # Example 7: Partial screenshot with selectors
        # Note: Another partial screenshot of the same URL with different selector
        yield UjeebuScrapeRequest(
            url='https://quotes.toscrape.com/',
            params={
                'response_type': 'screenshot',
                'screenshot_partial': '.quote:first-child',
                'js': True,
                'json': True,
            },
            dont_filter=True,  # Testing: same URL, same element selector
            callback=self.save_screenshot,
            meta={'screenshot_type': 'coordinates'}
        )

    def save_screenshot(self, response):
        """Save screenshot to file."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse screenshot response")
            return

        if not data.get('success', True):
            self.logger.error(f"Screenshot failed: {data.get('message')}")
            return

        # Get base64 screenshot data
        screenshot_b64 = data.get('screenshot')
        if not screenshot_b64:
            self.logger.error("No screenshot data in response")
            return

        # Decode and save
        screenshot_data = base64.b64decode(screenshot_b64)

        # Generate filename
        screenshot_type = response.meta.get('screenshot_type', 'unknown')
        domain = response.url.split('/')[2].replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain}_{screenshot_type}_{timestamp}.png"
        filepath = os.path.join(self.OUTPUT_DIR, filename)

        # Save file
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)

        self.logger.info(f"Saved screenshot: {filepath}")

        yield {
            'type': 'screenshot',
            'url': response.url,
            'screenshot_type': screenshot_type,
            'file': filepath,
            'size_bytes': len(screenshot_data),
        }

    def save_pdf(self, response):
        """Save PDF to file."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse PDF response")
            return

        if not data.get('success', True):
            self.logger.error(f"PDF generation failed: {data.get('message')}")
            return

        # Get base64 PDF data
        pdf_b64 = data.get('pdf')
        if not pdf_b64:
            self.logger.error("No PDF data in response")
            return

        # Decode and save
        pdf_data = base64.b64decode(pdf_b64)

        # Generate filename
        domain = response.url.split('/')[2].replace('.', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{domain}_{timestamp}.pdf"
        filepath = os.path.join(self.OUTPUT_DIR, filename)

        # Save file
        with open(filepath, 'wb') as f:
            f.write(pdf_data)

        self.logger.info(f"Saved PDF: {filepath}")

        yield {
            'type': 'pdf',
            'url': response.url,
            'file': filepath,
            'size_bytes': len(pdf_data),
        }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(ScreenshotSpider)
    process.start()
