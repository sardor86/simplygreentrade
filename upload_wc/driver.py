from woocommerce import API
import json
import logging
from tqdm import tqdm

from config import WoocommerceConfig

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


class WooCommerceDriver:

    def __init__(self, config: WoocommerceConfig) -> None:
        self.categories = []

        self.product_data = []

        self.api = API(
            url=config.wc_site,
            consumer_key=config.wc_key,
            consumer_secret=config.wc_secret,
            timeout=60
        )
        if self.api.get('products/categories').status_code == 200:
            logging.info('authorization successfully')
        else:
            logging.error('authorization error')

    def get_all_category(self) -> None:
        response = json.loads(self.api.get('products/categories').text)
        for category in response:
            self.categories.append({
                'id': category['id'],
                'name': category['name']
            })

    def get_category(self, name_category: str) -> int:
        for category in self.categories:
            if name_category == category['name']:
                return category['id']

    def delete_all_products(self):
        product_data = json.loads(self.api.get('products').text)

        logging.info('delete all products')
        for product in tqdm(product_data):
            self.api.delete(f'products/{product["id"]}')

    def create_category(self, categories_list: list) -> None:
        self.get_all_category()

        logging.info('deleted unnecessary categories')
        for category in tqdm(self.categories):
            if category['name'] in categories_list:
                categories_list.remove(category['name'])
            else:
                self.api.delete(f'products/categories/{category["id"]}')

        logging.info('create categories')
        for category in tqdm(categories_list):
            category_data = {
                "name": category,
                "description": "category description"
            }
            self.api.post('products/categories', category_data, params={'force': True})

        self.get_all_category()

    def add_products(self, products_list: list) -> None:
        self.delete_all_products()

        logging.info('create new products')
        for product in tqdm(products_list):
            product_data = {
                'name': product['name'],
                'description': product['description'],
                'regular_price': str(product['price']),
                'on_sale': product['is_available'],
                'stock_quantity': product['in_stock'],
                'meta_data': [{
                    'key': 'maximum_allowed_quantity',
                    'value': str(product['in_stock'])
                }],
                'categories': [
                    {
                        'id': self.get_category(product['category'])
                    }
                ],
                'images': [
                    {
                        'src': product['image']
                    }
                ],
                'attributes': [
                    {
                        'name': list(attribute.keys())[0],
                        'visible': True,
                        'variation': True,
                        'options': [
                            attribute[list(attribute.keys())[0]]
                        ]
                    }
                    for attribute in product['features']
                ]
            }
            self.api.post('products', product_data)
