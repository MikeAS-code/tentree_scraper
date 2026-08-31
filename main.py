from lxml import html, etree
from curl_cffi import requests
from curl_cffi.requests import RetryStrategy
import json

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
            for idx, page in enumerate(pages, start=1):
                print(f'Getting products from page #{idx}')
                self.get_products_from_page(page)

            print(f"The total number of URLs is: {len(self._records)}")
            return list(self._records)

        except Exception as e:
            print(f"There was an error on Discovery run - Error: {e}")


class PDP:

    def __init__(self):
        # count is extra attempts after the first; delay+jitter ≈ 2–4s on the first retry
        self._session = requests.Session(
            impersonate="chrome",
            verify=False,
            timeout=config.TIMEOUT,
            retry=RetryStrategy(count=config.MAX_RETRIES - 1, delay=2, jitter=2),
            raise_for_status=True,
        )

    def make_requests(self, url, status_code=200, payload=None, **kwargs):
        try:
            response = self._session.get(url, data=payload, **kwargs)
            if response.status_code == status_code:
                return response
        except Exception as e:
            print(f"There was an error making the request to the url {url} - Error: {e}")
        return None


    def parser_fields_product(self, data, url_product=None):
        try:
            def https(url):
                return f"https:{url}" if url and str(url).startswith("//") else (url or "")

            def money(cents):
                return cents / 100 if cents is not None else None

            description = data.get("description") or ""
            if description:
                try:
                    description = html.fromstring(description).text_content().strip()
                except Exception:
                    pass

            option = next((o.get("name") for o in data.get("options") or []), None)
            variants = [
                {
                    "id": v.get("id"),
                    "title": v.get("title"),
                    "sku": v.get("sku"),
                    "stock": v.get("available"),
                    "price": money(v.get("price")),
                    "image": https(
                        (v.get("featured_image") or {}).get("src")
                        if isinstance(v.get("featured_image"), dict)
                        else v.get("featured_image")
                    ),
                    "barcode": v.get("barcode"),
                    "option": option,
                    "value_option": v.get("option1"),
                }
                for v in data.get("variants") or []
            ]

            url = url_product or data.get("url") or ""
            if url.startswith("/"):
                url = f"{config.BASE_URL}{url}"

            return {
                "url": url,
                "id": data.get("id"),
                "title": data.get("title"),
                "description": description,
                "vendor": data.get("vendor"),
                "price": money(data.get("price")),
                "image_main": https(data.get("featured_image")),
                "images": [https(img) for img in data.get("images") or [] if img],
                "rating_reviews": None,
                "amount_reviews": None,
                "amount_variants": len(variants),
                "variants": variants,
            }

        except Exception as e:
            print(f"There was an error on parser_fields_product - Error: {e}")
            return None

    def parser_fields_reviews(self, html_content):
        try:
            tree = html.fromstring(html_content)
            scripts = tree.xpath('//script[@id="viewed_product"]/text()')
            if not scripts:
                return None, None

            script = scripts[0]
            marker = "MetafieldReviews = {"
            idx = script.find(marker)
            if idx == -1:
                return None, None

            reviews, _ = json.JSONDecoder().raw_decode(
                script[idx + len("MetafieldReviews = "):]
            )
            rating = reviews.get("rating") or {}
            rating_reviews = rating.get("value")
            amount_reviews = reviews.get("rating_count")

            if rating_reviews is not None:
                rating_reviews = float(rating_reviews)
            if amount_reviews is not None:
                amount_reviews = int(amount_reviews)

            return rating_reviews, amount_reviews

        except Exception as e:
            print(f"There was an error on parser_fields_reviews - Error: {e}")
            return None, None

    def get_product_detail(self, url_product):
        try:
            response = self.make_requests(
                f"{url_product}.js",
                proxies=config.PROXIES,
                headers=config.HEADERS_PDP,
            )
            if not response:
                return None

            data = response.json()
            product = self.parser_fields_product(data, url_product)
            if not product:
                return None

            html_response = self.make_requests(
                url_product,
                proxies=config.PROXIES,
                headers=config.HEADERS_PDP,
            )
            if html_response:
                rating_reviews, amount_reviews = self.parser_fields_reviews(
                    html_response.text
                )
                product["rating_reviews"] = rating_reviews
                product["amount_reviews"] = amount_reviews

            return product

        except Exception as e:
            print(f"There was an error on get_product_detail - Error: {e}")
            return None




    def run(self, products):
        records = []
        for index, url in enumerate(products, start=1):
            print(f"Product #{index}/{len(products)}")
            product = self.get_product_detail(url)
            if product:
                records.append(product)

        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        print(f"Saved {len(records)} products to products.json")
        return records



if __name__ == "__main__":
    print("Start crawler")
    products = Discovery().run() or []

    PDP().run(products)

    print("End crawler")
