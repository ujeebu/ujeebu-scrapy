import logging

from scrapy import Request
from scrapy.exceptions import NotConfigured

from .ujeebu_request import UjeebuRequest

log = logging.getLogger('scrapy.ujeebu')

class UjeebuMiddleware(object):
    def __init__(self, settings):
        self.enabled = settings.get('UJEEBU_ENABLED', True)
        self.api_key = settings.get('UJEEBU_API_KEY')
        if self.enabled and not self.api_key:
            log.error(f'[UjeebuAPI] API key not found')
            raise NotConfigured
        self.base_url = 'https://api.ujeebu.com'
        if self.enabled:
            log.info(f'[UjeebuAPI] Ujeebu API is enabled')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        """Process a request using the proxycrawl API if applicable"""

        if not self.enabled:
            log.warning('Skipping Ujeebu Scrape API!')
            return None

        if not isinstance(request, UjeebuRequest):
            return None

        ujeebu_params = request.query_params
        ujeebu_url = self._build_ujeebu_url(ujeebu_params)

        log.debug(f'[UjeebuAPI] Override request URL with ujeebu\'s one {ujeebu_url}')

        return request.replace(cls=Request, url=ujeebu_url, meta=request.meta)

    def process_response(self, request, response, spider):
        """Process a response coming from proxycrawl API if applicable"""

        if 'ujeebu' not in request.meta:
            return response

        # Replace url again with the original url saved in request
        log.debug(f'[UjeebuAPI] Response overridden with URL: {request.url}')

        return response.replace(url=request.meta['ujeebu']['url'])

    def _build_ujeebu_url(self, query_params):
        qs_params = {
            'apikey': self.api_key,
        }
        qs_params.update(query_params)

        qs = '&'.join(f'{k}={v}' for k, v in qs_params.items())

        return f'{self.base_url}/scrape?{qs}'
