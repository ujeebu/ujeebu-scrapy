"""
Complete E-Commerce Data Pipeline Example

This comprehensive example demonstrates how to combine all three Ujeebu APIs
(SERP, Scrape, Extract) to build a complete data collection pipeline.

Use Case: Competitive Intelligence
1. Search Google for product reviews
2. Scrape product listing pages
3. Extract article content from review sites
4. Collect structured data for analysis

Run with: scrapy runspider ecommerce_pipeline_spider.py -o data.json
"""

import json
from datetime import datetime
from urllib.parse import urljoin

import scrapy
import os
from ujeebu_scrapy import (
    UjeebuScrapeRequest,
    UjeebuExtractRequest,
    UjeebuSerpRequest,
)


class EcommercePipelineSpider(scrapy.Spider):
    """
    A comprehensive spider demonstrating all Ujeebu APIs working together.

    Pipeline:
    1. SERP: Search for product reviews
    2. Extract: Get article content from review sites
    3. Scrape: Get product details from e-commerce sites
    """

    name = 'ecommerce_pipeline'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'ujeebu_scrapy.UjeebuMiddleware': 543,
        },
        'UJEEBU_ENABLED': True,
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),

        # Scrapy settings
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 0.5,
        'LOG_LEVEL': 'INFO',

        # Retry settings
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408],
    }

    # Products to research
    products = [
        'iPhone 15 Pro review',
        'Sony WH-1000XM5 review',
        'MacBook Pro M3 review',
    ]

    def start_requests(self):
        """Start the pipeline with SERP searches."""
        for product in self.products:
            # Step 1: Search for reviews
            yield UjeebuSerpRequest(
                search=product,
                search_type='search',
                lang='en',
                location='us',
                results_count=10,
                callback=self.parse_serp_results,
                meta={
                    'product': product,
                    'step': 'serp'
                }
            )

            # Also search for news
            yield UjeebuSerpRequest(
                search=product,
                search_type='news',
                lang='en',
                location='us',
                results_count=5,
                callback=self.parse_news_results,
                meta={
                    'product': product,
                    'step': 'news_serp'
                }
            )

    def parse_serp_results(self, response):
        """Parse SERP results and dispatch to appropriate handlers."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse SERP response")
            return

        product = response.meta['product']

        # Yield SERP metadata
        metadata = data.get('metadata', {})
        yield {
            'type': 'serp_metadata',
            'product': product,
            'total_results': metadata.get('number_of_results'),
            'search_time': metadata.get('results_time'),
            'timestamp': datetime.now().isoformat(),
        }

        # Process organic results
        for result in data.get('organic_results', [])[:5]:
            link = result.get('link', '')
            title = result.get('title', '')

            # Determine the type of page and route accordingly
            if self._is_review_site(link):
                # Use Extract API for article/review content
                yield UjeebuExtractRequest(
                    url=link,
                    text=True,
                    html=True,
                    author=True,
                    pub_date=True,
                    is_article=True,
                    callback=self.parse_review_article,
                    meta={
                        'product': product,
                        'serp_title': title,
                        'serp_position': result.get('position'),
                        'step': 'extract'
                    }
                )
            elif self._is_ecommerce_site(link):
                # Use Scrape API with extract_rules for product data
                yield UjeebuScrapeRequest(
                    url=link,
                    js=True,
                    wait_for=2000,
                    extract_rules=self._get_product_extract_rules(),
                    callback=self.parse_product_page,
                    meta={
                        'product': product,
                        'serp_title': title,
                        'serp_position': result.get('position'),
                        'step': 'scrape_product'
                    }
                )
            else:
                # Generic page scraping
                yield UjeebuScrapeRequest(
                    url=link,
                    js=True,
                    wait_for=1000,
                    callback=self.parse_generic_page,
                    meta={
                        'product': product,
                        'serp_title': title,
                        'serp_position': result.get('position'),
                        'step': 'scrape_generic'
                    }
                )

    def parse_news_results(self, response):
        """Parse news search results."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return

        product = response.meta['product']

        for result in data.get('news_results', data.get('organic_results', [])):
            link = result.get('link', '')

            # Extract article content
            yield UjeebuExtractRequest(
                url=link,
                text=True,
                html=False,
                author=True,
                pub_date=True,
                is_article=True,
                quick_mode=True,  # Faster for news
                callback=self.parse_news_article,
                params={'mode': 'd144dd3'},
                meta={
                    'product': product,
                    'source': result.get('source') or result.get('site_name'),
                    'news_date': result.get('date'),
                    'step': 'extract_news'
                }
            )

    def parse_review_article(self, response):
        """Parse extracted review article content."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse article response")
            return

        # Extract article data from the 'article' field
        article = data.get('article', {})

        # Check if it's actually an article
        is_article = article.get('is_article', 0)
        if is_article < 0.5:
            self.logger.info(f"Skipping non-article: {response.url}")
            return

        yield {
            'type': 'review_article',
            'product': response.meta.get('product'),
            'url': response.url,
            'serp_position': response.meta.get('serp_position'),
            'title': article.get('title'),
            'author': article.get('author'),
            'pub_date': article.get('pub_date'),
            'is_article_score': is_article,
            'word_count': len(article.get('text', '').split()),
            'text_preview': article.get('text', '')[:500] if article.get('text') else None,
            'main_image': article.get('main_image'),
            'images_count': len(article.get('images', [])),
            'timestamp': datetime.now().isoformat(),
        }

    def parse_news_article(self, response):
        """Parse extracted news article."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            return

        # Extract article data from the 'article' field
        article = data.get('article', {})

        if article.get('is_article', 0) < 0.5:
            return

        yield {
            'type': 'news_article',
            'product': response.meta.get('product'),
            'url': response.url,
            'source': response.meta.get('source'),
            'news_date': response.meta.get('news_date'),
            'title': article.get('title'),
            'author': article.get('author'),
            'pub_date': article.get('pub_date'),
            'text_preview': article.get('text', '')[:300] if article.get('text') else None,
            'timestamp': datetime.now().isoformat(),
        }

    def parse_product_page(self, response):
        """Parse product page with extracted data."""
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error(f"Failed to parse product response")
            return

        if not data.get('success'):
            self.logger.error(f"Extraction failed: {data.get('message')}")
            return

        result = data.get('result', {})

        yield {
            'type': 'product',
            'search_product': response.meta.get('product'),
            'url': response.url,
            'serp_position': response.meta.get('serp_position'),
            'name': result.get('name'),
            'price': result.get('price'),
            'original_price': result.get('original_price'),
            'rating': result.get('rating'),
            'reviews_count': result.get('reviews_count'),
            'availability': result.get('availability'),
            'description': result.get('description'),
            'features': result.get('features', []),
            'images': result.get('images', []),
            'timestamp': datetime.now().isoformat(),
        }

    def parse_generic_page(self, response):
        """Parse generic page content."""
        yield {
            'type': 'page',
            'product': response.meta.get('product'),
            'url': response.url,
            'serp_position': response.meta.get('serp_position'),
            'serp_title': response.meta.get('serp_title'),
            'page_title': response.css('title::text').get(),
            'meta_description': response.css('meta[name="description"]::attr(content)').get(),
            'h1': response.css('h1::text').get(),
            'timestamp': datetime.now().isoformat(),
        }

    def _is_review_site(self, url):
        """Check if URL is from a known review site."""
        review_domains = [
            'techcrunch.com', 'theverge.com', 'cnet.com', 'engadget.com',
            'wired.com', 'tomsguide.com', 'pcmag.com', 'imore.com',
            'androidcentral.com', 'zdnet.com', 'arstechnica.com',
        ]
        return any(domain in url.lower() for domain in review_domains)

    def _is_ecommerce_site(self, url):
        """Check if URL is from a known e-commerce site."""
        ecommerce_domains = [
            'amazon.com', 'bestbuy.com', 'walmart.com', 'target.com',
            'newegg.com', 'bhphotovideo.com', 'adorama.com',
        ]
        return any(domain in url.lower() for domain in ecommerce_domains)

    def _get_product_extract_rules(self):
        """Return extract rules for product pages."""
        return {
            'name': {
                'selector': 'h1, [data-product-name], .product-title, .product-name',
                'type': 'text'
            },
            'price': {
                'selector': '.price, .product-price, [data-price], .a-price .a-offscreen',
                'type': 'text'
            },
            'original_price': {
                'selector': '.was-price, .original-price, .list-price, .a-text-strike',
                'type': 'text'
            },
            'rating': {
                'selector': '.rating, .star-rating, [data-rating], .a-icon-star',
                'type': 'text'
            },
            'reviews_count': {
                'selector': '.reviews-count, .review-count, #acrCustomerReviewText',
                'type': 'text'
            },
            'availability': {
                'selector': '.availability, .stock-status, #availability',
                'type': 'text'
            },
            'description': {
                'selector': '.product-description, .description, #productDescription',
                'type': 'text'
            },
            'features': {
                'selector': '.feature-bullets li, .product-features li, #feature-bullets li',
                'type': 'text',
                'multiple': True
            },
            'images': {
                'selector': '.product-image img, .gallery img, #main-image',
                'type': 'image',
                'multiple': True
            }
        }


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess

    process = CrawlerProcess({
        'LOG_LEVEL': 'INFO',
    })
    process.crawl(EcommercePipelineSpider)
    process.start()
