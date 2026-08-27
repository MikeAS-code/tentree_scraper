from dotenv import load_dotenv
import os
import re

load_dotenv('.env')

PROXY=os.environ.get('PROXY')

PROXIES={
    'http':PROXY,
    'https':PROXY
}

BASE_URL='https://www.tentree.com'


PRODUCT_SITEMAP_PATTERN = re.compile(
    r"^https://www\.tentree\.com/sitemap_products_\d+\.xml\?from=\d+&to=\d+$"
)

PRODUCT_PATTERN = re.compile(
    r"^https://www\.tentree\.com/products/[^/?#]+/?$"
)

TIMEOUT=30

MAX_RETRIES=3


HEADERS_PDP = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'if-none-match': '"page_cache:23413995:ProductDetailsController:7bfbb8d54189a2d8959d11001f53e0cf:fe0dc2a6008f96b39a014f2d4b4fbbec"',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-ch-viewport-width': '1366',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36', 
}