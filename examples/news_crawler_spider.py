"""
News Crawler Spider Example

A more comprehensive news crawler that combines Scrape and Extract APIs.

This spider:
1. Scrapes a news homepage to find article links
2. Extracts full article content from each link

Run with: scrapy runspider news_crawler_spider.py -o news_articles.json
"""

import scrapy
import os
from ujeebu_scrapy import UjeebuExtractRequest, UjeebuScrapeRequest


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
        'UJEEBU_API_KEY': os.environ.get('UJEEBU_API_KEY'),
        'UJEEBU_BASE_URL': os.environ.get('UJEEBU_BASE_URL', 'https://api.ujeebu.com'),
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
    process.crawl(NewsCrawlerSpider)
    process.start()

