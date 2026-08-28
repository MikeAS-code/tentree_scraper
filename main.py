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
        self._records=[]

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

    def get_product_reviews(self, id, title, type, sku):

        if id and title and type and sku:
            params_reviews = {
                        'productId': id,
                        'productName': title,
                        "productType": type,
                        'productSKU': sku,
                        'page': '1',
                        'apiKey': 'pubkey-LO1Xa8x73gKEGHN3Wryy0ivU11p2tu',
                        'sId': '32040',
                        'take': '5',
                        'sort': 'recent',
                        'widgetLanguage': 'en',
                    }

            try:
                response=self.make_requests(config.BASE_URL_REVIEWS,
                                            proxies=config.PROXIES,
                                            headers=config.HEADERS_REVIEWS,
                                            params=params_reviews)
                if response:
                    data=response.json()
                    return data

            except Exception as e:
                print(f'There was an error on get_product_detail - Error: {e}')
        else:
            return []

    def extract_variants(self, variants, options):

        extracted_variants = []

        for variant in variants:

            try:
                id = int(variant["id"])
                if not id:
                    id = 0
            except:
                id = 0

            try:
                title = variant["title"]
                if not title:
                    title = ''
            except:
                title = ''

            try:
                sku = variant["sku"]
                if not sku:
                    sku = ''
            except:
                sku = ''

            try:
                stock = variant["available"]
            except:
                stock = False

            try:
                price = float(variant["price"])
                if not price:
                    price = 0
            except:
                price = 0

            try:
                image = variant["featured_image"]["src"]
                if not image:
                    image = ''
            except:
                image = ''

            try:
                barcode = variant["barcode"]
                if not barcode:
                    barcode = ''
            except:
                barcode = ''

            try:
                option = [
                    options[i]["name"]
                    for i in range(len(variant["options"]))
                ]
                if not option:
                    option = []
            except:
                 option = []

            try:
                value_option = variant["options"]
                if not value_option:
                    value_option = []
            except: 
                value_option = []

            record = {
                        "id": id,
                        "title": title,
                        "sku": sku,
                        "stock": stock,
                        "price": price,
                        "image": image,
                        "barcode": barcode,
                        "option": option,
                        "value_option": value_option,
                    }
            
            extracted_variants.append(record)

        return extracted_variants

    def parser_fields_product(self,data, url_product):
        try:
            
            try:
                url = url_product
                if not url:
                    url = ''
            except:
                url = ''

            try:
                id = data['id']
                if not id:
                    id = ''
            except:
                id = ''

            try:
                title=data['title']
                if not title:
                    title = ''
            except:
                title = ''

            try:
                raw_description = data['description']
                description = raw_description.replace('<p>','').replace('</p>', '')
                if not description:
                    description = ''
            except:
                description = ''

            try:
                vendor = data['vendor']
                if not vendor:
                    vendor = ''
            except:
                vendor = ''

            try:
                price=data['price']
                if not price:
                    price = 0
            except:
                price = 0

            try:
                imagen_main = data['featured_image']
                if not imagen_main:
                    imagen_main = ''

            except:
                imagen_main = ''

            try:
                images = data['images']
                if not images:
                    images = []

            except:
                images = []
            
            try:
                type = data["type"]
                if not type:
                    type = ''
            except:
                type = ''

            try:
                sku = data["variants"][0]["sku"]
                if not sku:
                    sku = ''
            except:
                sku = ''
           

            try:
                response_reviews = self.get_product_reviews(id, title, type,sku)

                if response_reviews:
                    rating_reviews = float(response_reviews['rating'])
                    amount_reviews = int(response_reviews['count'])
                    if not rating_reviews:
                        rating_reviews = 0
                    if not amount_reviews:
                        amount_reviews = 0
                else:
                    rating_reviews = 0
                    amount_reviews = 0
            except:
                rating_reviews = 0
                amount_reviews = 0

            try:
                amount_variants = len(data['variants'])
                if not amount_variants:
                    amount_variants = 0
            except:
                amount_variants = 0

            try:
                variants = self.extract_variants(data['variants'], data['options'])
                if not variants:
                    variants = []
            except:
                variants = []

            record = {
                "url":url,
                "id":id,
                "title":title,
                "description":description,
                "vendor":vendor,
                "price":price,
                "imagen_main":imagen_main,
                "images":images,
                "rating_reviews":rating_reviews,
                "amount_reviews":amount_reviews,
                "amount_variants":amount_variants,
                "variants":variants
            }

            self._records.append(record)
        
        except Exception as e:
            print(f'error - {e}')

    def get_product_detail(self,url_product):
        try:
            response=self.make_requests(f'{url_product}.js',
                                        proxies=config.PROXIES,
                                        headers=config.HEADERS_PDP)
            if response:
                data=response.json()
                self.parser_fields_product(data, url_product)

        except Exception as e:
            print(f'There was an error on get_product_detail - Error: {e}')




    def run(self, products):

        for index, product in enumerate(products[0:3],start=1):
            print(f'Product #{index}/{len(products)}')
            self.get_product_detail(product)

        print(self._records)



if __name__ == "__main__":
    print("Start crawler")
    products = Discovery().run()

    PDP().run(products)

    print("End crawler")
