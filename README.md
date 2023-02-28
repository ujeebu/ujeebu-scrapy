# Ujeebu API middleware for Scrapy

The `ujeebu_scrapy` is a Python library that acts as a middleware for [Scrapy](http://scrapy.org/), to process requests using [Ujeebu Scrape API](https://ujeebu.com/scrape).

## Installing

Choose a way of installing:

- Clone the repository inside your Scrapy project and run the following:

```bash
git clone https://github.com/ujeebu/ujeebu-scrapy.git
python3 setup.py install
```

- Or use pip:

```bash
pip install ujeebu-scrapy
```

## Usage

To use `ujeebu_scrapy`, add it to your Scrapy project's `settings.py` file:

```python
# Enable the middleware
DOWNLOADER_MIDDLEWARES = {
    "ujeebu_scrapy.UjeebuMiddleware": 543,
}
```

Next, Enable Ujeebu and add your Ujeebu API KEY to your Scrapy project's `settings.py` file:
```python
# Enable Ujeebu
UJEEBU_ENABLED = True

# The Ujeebu API key
UJEEBU_API_KEY = '__YOUR-API-KEY__'
```

Finally, in your spiders use `ujeebu_scrapy.UjeebuRequest` instead of the built-in scrapy Request
`UjeebuRequest` accepts the url as a first argument, a dict of [scrape API params](https://ujeebu.com/docs/scrape#parameters) as second argument and dict of custom headers as third argument.
```python
import scrapy
from ujeebu_scrapy import UjeebuRequest

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = ['https://www.example.com']

    custom_settings = {}

    def start_requests(self):
        url = 'https://www.example.com'
        yield UjeebuRequest(url=url, params={
            'response_type': 'html',
            'js': True,
            'proxy': 'premium'
        }, headers={
            "Authorization": "Basic eWSjaW5lnlhY4luZUdxMDE2"
        }, meta={}, callback=self.parse)

    def parse(self, response):
        # Your spider logic goes here
        pass
```

That's it! The middleware will automatically send your spider's requests data through the Ujeebu Scrape API.

## Contributing
Contributions are welcome! Please feel free to submit a pull request or open an issue if you encounter any problems or have any suggestions for improvement.

## License
This library is licensed under the MIT License. See the LICENSE file for more information.
