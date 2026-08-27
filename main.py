import pandas as pd
from lxml import html, etree
from curl_cffi import requests
import time
import random

import config


class Discovery:

    def __init__(self):
        self._records = set()

    def get_products_from_page(self, page):

        try:

            res = requests.get(
                page,
                impersonate="chrome",
                verify=False,
                proxies=config.PROXIES,
                timeout=config.TIMEOUT,
            )

            if res and res.status_code == 200:

                tree = etree.fromstring(res.content)
                # Sitemap XML normalmente utiliza namespace
                urls = tree.xpath(
                    "//sm:loc/text()",
                    namespaces={"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                )

                for url in urls:
                    if config.PRODUCT_PATTERN.fullmatch(url):
                        self._records.add(url)

        except Exception as e:
            print(f"There was an error on get_pages_from_sitemap - Error: {e}")

    def get_pages_from_sitemap(self):
        try:
            res = requests.get(
                f"{config.BASE_URL}/sitemap.xml",
                impersonate="chrome",
                verify=False,
                proxies=config.PROXIES,
                timeout=config.TIMEOUT,
            )

            if res and res.status_code == 200:

                tree = etree.fromstring(res.content)
                # Sitemap XML normalmente utiliza namespace
                urls = tree.xpath(
                    "//sm:loc/text()",
                    namespaces={"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"},
                )

                pages = []
                for url in urls:
                    if config.PRODUCT_SITEMAP_PATTERN.fullmatch(url):
                        pages.append(url)

                return pages

            return []

        except Exception as e:
            print(f"There was an error on get_pages_from_sitemap - Error: {e}")
            return []

    def run(self):
        try:
            print('Extracting pages')
            pages = self.get_pages_from_sitemap()
            for idx,page in enumerate(pages[0:2],start=1):
                print(f'Getting products from page #{idx}')
                self.get_products_from_page(page)

            print(f"The total number of URLs is: {len(self._records)}")
            return list(self._records)

        except Exception as e:
            print(f"There was an error on Discovery run - Error: {e}")


class PDP:

    def __init__(self):
        pass

    def make_requests(
        self,
        url,
        status_code=200,
        proxies={},
        headers={},
        cookies={},
        payload={},
        params={},
        impersonate="chrome",
        verify=False,
        timeout=30,
    ):
        attempt = 0
        while attempt < config.MAX_RETRIES:
            try:
                response =requests.get(
                    url,
                    proxies=proxies,
                    headers=headers,
                    cookies=cookies,
                    params=params,
                    data=payload,
                    impersonate=impersonate,
                    verify=verify,
                    timeout=timeout,
                )

                if response and response.status_code == status_code:
                    return response
                else:
                    raise Exception('There was an error on response')

            except Exception as e:
                attempt+=1
                print(f"Attempt {attempt} Error: {e}")
                time.sleep(random.randint(2, 4))

        print('Max retries reached')
        return None


    def parser_fields_product(self,data):
        try:
            title=data['title']
            price=data['price']

            #sacar el resto de campos
            
            print(title)
            print(price)

        except Exception as e:
            print('errror - {e}')

    def get_product_detail(self,url_product):
        try:
            response=self.make_requests(f'{url_product}.js',
                                        proxies=config.PROXIES,
                                        headers=config.HEADERS_PDP)
            if response:
                data=response.json()
                self.parser_fields_product(data)

        except Exception as e:
            print(f'There was an error on get_product_detail - Error: {e}')




    def run(self, products):

        for index, product in enumerate(products[0:1],start=1):
            print(f'Product #{index}/{len(products)}')
            self.get_product_detail(product)



if __name__ == "__main__":
    print("Start crawler")
    products = Discovery().run()

    PDP().run(products)

    print("End crawler")
