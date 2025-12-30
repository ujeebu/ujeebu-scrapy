# Ujeebu Scrapy Examples

This directory contains example spiders demonstrating various features of the Ujeebu Scrapy middleware.

## Running Examples

### Prerequisites

1. Install ujeebu-scrapy:
```bash
pip install ujeebu-scrapy
```

2. Set your API key:
```bash
export UJEEBU_API_KEY="your-api-key"
export UJEEBU_BASE_URL="https://api.ujeebu.com"  # Optional, defaults to this
```

### Running Individual Spiders

Each spider can be run directly with Python:

```bash
python basic_scrape_spider.py
```

Or using Scrapy's runspider command:

```bash
scrapy runspider basic_scrape_spider.py -o output.json
```

## Available Spiders

### Basic Examples

#### 1. **basic_scrape_spider.py**
Basic web scraping with the Ujeebu Scrape API.
- Simple HTTP requests
- JavaScript rendering
- Custom headers and cookies
- Wait conditions
- Multiple request examples

**Run:**
```bash
python basic_scrape_spider.py
```

#### 2. **extract_rules_spider.py**
Demonstrates structured data extraction using extract_rules.
- CSS selector-based extraction
- Multiple item extraction
- Nested object extraction
- Pagination with extract_rules
- E-commerce product scraping

**Run:**
```bash
python extract_rules_spider.py
```

#### 3. **ujeebu_blog_spider.py**
A practical blog crawler example.
- Crawls blog homepage
- Extracts article links
- Scrapes individual articles
- Demonstrates link following

**Run:**
```bash
python ujeebu_blog_spider.py
```

### SERP (Search Engine) Examples

#### 4. **serp_basic_spider.py**
Google search using the SERP API.
- Web search
- News search
- Image search
- Video search
- Location-specific searches
- Pagination

**Run:**
```bash
python serp_basic_spider.py
```

#### 5. **serp_and_scrape_spider.py**
Combines SERP and Scrape APIs.
- Search Google for URLs
- Scrape each result page
- Extract metadata from pages

**Run:**
```bash
python serp_and_scrape_spider.py
```

#### 6. **geo_serp_spider.py**
Geo-targeted search results.
- Search from different countries
- Multiple languages
- Local SEO analysis
- Competitor research

**Run:**
```bash
python geo_serp_spider.py
```

### Article Extraction Examples

#### 7. **article_basic_spider.py**
Extract article content from news sites.
- Article title, author, date
- Main text and HTML
- Images and media
- Quick mode for faster extraction
- JavaScript rendering support

**Run:**
```bash
python article_basic_spider.py
```

#### 8. **news_crawler_spider.py**
News aggregator crawler.
- Crawls Hacker News homepage
- Extracts article links
- Gets full article content
- Filters by article probability

**Run:**
```bash
python news_crawler_spider.py
```

### Infinite Scroll & Dynamic Content

#### 9. **infinite_scroll_basic_spider.py**
Handle infinite scroll pages.
- Basic scrolling
- Progressive scroll (until content stops)
- Scroll to specific element
- Custom scroll callbacks
- "Load More" button clicking

**Run:**
```bash
python infinite_scroll_basic_spider.py
```

#### 10. **ecommerce_scroll_spider.py**
E-commerce product scraping with infinite scroll.
- Handles lazy-loaded products
- Progressive scrolling
- Extract product data with rules
- Multiple category support

**Run:**
```bash
python ecommerce_scroll_spider.py
```

#### 11. **ecommerce_pipeline_spider.py**
Complete e-commerce scraping pipeline.
- List page scraping
- Product detail page scraping
- Extract structured product data
- Price, rating, availability

**Run:**
```bash
python ecommerce_pipeline_spider.py
```

### Advanced Features

#### 12. **screenshot_spider.py**
Take screenshots of web pages.
- Full page screenshots
- Partial screenshots
- Element screenshots
- PDF generation
- Screenshot with scrolling

**Run:**
```bash
python screenshot_spider.py
```

#### 13. **proxy_basic_spider.py**
Proxy and geo-targeting features.
- Different proxy types (rotating, premium, residential, mobile)
- Country-specific proxies
- Session-based sticky proxies
- Auto-proxy fallback
- IP verification

**Run:**
```bash
python proxy_basic_spider.py
```

## Common Patterns


### Basic Scraping
```python
yield UjeebuScrapeRequest(
    url='https://example.com',
    js=True,
    wait_for=2000,
    callback=self.parse
)
```

### Extract Rules
```python
yield UjeebuScrapeRequest(
    url='https://example.com/products',
    extract_rules={
        'products': {
            'selector': '.product',
            'type': 'obj',
            'multiple': True,
            'children': {
                'name': {'selector': '.name', 'type': 'text'},
                'price': {'selector': '.price', 'type': 'text'}
            }
        }
    },
    callback=self.parse_products
)
```

### SERP Search
```python
yield UjeebuSerpRequest(
    search='python web scraping',
    search_type='search',
    lang='en',
    location='us',
    callback=self.parse_results
)
```

### Article Extraction
```python
yield UjeebuExtractRequest(
    url='https://example.com/article',
    text=True,
    html=True,
    author=True,
    pub_date=True,
    callback=self.parse_article
)
```

## Troubleshooting

### Spider Not Producing Data

1. Check your API key is set:
```bash
echo $UJEEBU_API_KEY
```

2. Check the spider's custom_settings for correct middleware setup

3. Enable debug logging:
```bash
scrapy runspider spider.py -L DEBUG
```

### Import Errors

Make sure ujeebu-scrapy is installed:
```bash
pip install ujeebu-scrapy
```

### Timeout Issues

Increase the timeout in custom_settings:
```python
custom_settings = {
    'UJEEBU_DEFAULT_TIMEOUT': 120,  # seconds
}
```

## Additional Resources

- [Ujeebu API Documentation](https://docs.ujeebu.com)
- [Scrapy Documentation](https://docs.scrapy.org)
- [ujeebu-scrapy GitHub](https://github.com/ujeebu/ujeebu-scrapy)

## Contributing

Feel free to submit additional example spiders or improvements via pull requests!

