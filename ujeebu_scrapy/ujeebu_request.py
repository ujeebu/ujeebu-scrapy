import copy
import logging
import urllib
from urllib.parse import quote_plus

from scrapy import Request

from scrapy.spidermiddlewares.httperror import HttpError

log = logging.getLogger('scrapy.ujeebu')


class UjeebuRequest(Request):

    def __init__(self, url,
                 params={},
                 headers=None,
                 meta=None,
                 body=None,
                 **kwargs):
        meta = copy.deepcopy(meta) or {}

        if headers:
            headers = self.handle_headers(headers)

        query_params = self.handle_ujeebu_params({
            **{'url': url},
            **params
        })

        self.query_params = query_params

        meta['ujeebu'] = {
            'url': url
        }

        errback = kwargs.pop("errback", self.handle_error)

        super().__init__(
            url,
            headers=headers,
            body=body,
            meta=meta,
            errback=errback,
            **kwargs
        )

    def get_query_params(self):
        return self.query_params

    @staticmethod
    def handle_url(url):
        return urllib.parse.quote(url)

    @staticmethod
    def handle_custom_js(js):
        return urllib.parse.quote(js)
        # return base64.b64encode(s.encode()).decode()

    @staticmethod
    def handle_headers(headers):
        return {f'Ujb-{k}': v for k, v in headers.items()}

    @staticmethod
    def handle_cookies(cookies):
        if isinstance(cookies, dict):
            stringified_cookies = ';'.join(f'{k}={v}' for k, v in cookies.items())
            return urllib.parse.quote(stringified_cookies)
        elif isinstance(cookies, list):
            # Ujeebu only supports name=value cookies ATM
            raise NotImplementedError
        elif isinstance(cookies, str):
            return cookies

    @classmethod
    def handle_ujeebu_params(cls, params):
        new_params = {}
        for k, v in params.items():
            if v in (None, '', [], {}):
                continue
            elif k == 'url':
                new_params[k] = cls.handle_url(v)
            elif k == 'custom_js':
                new_params[k] = cls.handle_custom_js(v)
            elif k == 'cookies':
                new_params[k] = cls.handle_cookies(v)
            else:
                new_params[k] = v
        return new_params

    def handle_error(self, error):
        if error.check(HttpError):
            log.error(
                f'Received an Ujeebu error: {error.value.response.text}')
        else:
            log.error(repr(error))
