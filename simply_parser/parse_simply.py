import json
import logging
import concurrent.futures
import math
from tqdm import tqdm
from bs4 import BeautifulSoup

from simply_parser.utils import get_session
from config import load_simply_config, SIMPLY_PARSER_HEADERS, SIMPLY_PARSER_BASE_URL, \
    SIMPLY_PARSER_AUTH_URL, SIMPLY_PARSER_ITEMS_PER_PAGE

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)


class SimplyGreenTrade:
    """
    Interaction with https://simplygreentrade.com/
    """

    def __init__(self, path):
        self.path = path
        self.config = load_simply_config(self.path / '.env')
        self.session = get_session()
        self.__auth()
        self.catalog_urls = []
        self.product_urls = []

    def __auth(self):
        """
        Authorization
        """
        response = self.session.get(SIMPLY_PARSER_AUTH_URL, headers=SIMPLY_PARSER_HEADERS)
        soup = BeautifulSoup(response.text, 'lxml')

        login_nonce = soup.find('input', {'id': 'woocommerce-login-nonce'})['value']
        data = f'username={self.config.simply_login}&' \
               f'password={self.config.simply_password}&' \
               f'woocommerce-login-nonce={login_nonce}&_wp_http_referer=%2Faccount%2F%3Faction%3Dlogin&login=Log+in'
        response = self.session.post(SIMPLY_PARSER_AUTH_URL, headers=SIMPLY_PARSER_HEADERS, data=data)

        if response.status_code != 200:
            raise ValueError("Login or password is incorrect")
        logging.info('Successful authorization')

    def _get_catalog_urls(self):
        """
        Finds all catalogs links
        """
        response = self.session.get(SIMPLY_PARSER_BASE_URL)
        soup = BeautifulSoup(response.text, 'lxml')
        self.catalog_urls = [x.find('a')['href']
                             for x in soup.find('ul',
                             {'id': 'menu-desktop-horizontal-menu'}).find_all('li',
                                                                              class_='item-level-0')[:-1]]

    def _get_product_urls(self):
        """
        Finds all product links
        """
        def parse_per_page(page_strip: str, pages_count: int, catalog: str):
            logging.info(f'Total pages: {pages_count}')
            for page in range(1, pages_count+1):
                url = catalog + f'{page_strip}{page}'
                response = self.session.get(url)
                soup = BeautifulSoup(response.text, 'lxml')
                cur_product_urls = [x.find('a')['href'] for x in soup.find_all('div', class_='product-element-top')]
                for cur_product_url in cur_product_urls:
                    if cur_product_url not in self.product_urls:
                        self.product_urls.append(cur_product_url)

        for catalog in tqdm(self.catalog_urls):
            logging.info(f'Start parsing {catalog}')
            response = self.session.get(catalog)
            soup = BeautifulSoup(response.text, 'lxml')

            try:
                product_count = soup.find('p', class_='woocommerce-result-count').text.strip()
                product_count = int(product_count.replace('Showing 1–24 of ', '').replace(' results', ''))
            except:
                product_count = None

            if product_count:
                pages_count = math.ceil(product_count / SIMPLY_PARSER_ITEMS_PER_PAGE)
                page_strip = 'page/'
                parse_per_page(page_strip, pages_count, catalog)
            elif 'bestsellers' in catalog:
                pages_count = int(soup.find('ul', class_='page-numbers').find_all('li')[-2].text)
                page_strip = '?product-page='
                parse_per_page(page_strip, pages_count, catalog)
            elif 'new' in catalog:
                logging.info('Unable to find products counter')
                page = 0
                while True:
                    page += 1
                    data = {
                        'atts[element_title]': '',
                        'atts[post_type]': 'product',
                        'atts[layout]': 'grid',
                        'atts[include]': '',
                        'atts[custom_query]': '',
                        'atts[taxonomies]': '',
                        'atts[pagination]': 'infinit',
                        'atts[items_per_page]': '25',
                        'atts[product_hover]': 'standard',
                        'atts[spacing]': '20',
                        'atts[columns]': '5',
                        'atts[columns_tablet]': '3',
                        'atts[columns_mobile]': '2',
                        'atts[sale_countdown]': '0',
                        'atts[stretch_product_desktop]': '0',
                        'atts[stretch_product_tablet]': '0',
                        'atts[stretch_product_mobile]': '0',
                        'atts[stock_progress_bar]': '0',
                        'atts[highlighted_products]': '0',
                        'atts[products_bordered_grid]': '0',
                        'atts[products_bordered_grid_style]': 'outside',
                        'atts[products_with_background]': '0',
                        'atts[products_shadow]': '0',
                        'atts[products_color_scheme]': 'default',
                        'atts[product_quantity]': '0',
                        'atts[grid_gallery]': '',
                        'atts[grid_gallery_control]': '',
                        'atts[grid_gallery_enable_arrows]': '',
                        'atts[offset]': '',
                        'atts[orderby]': 'date',
                        'atts[query_type]': 'OR',
                        'atts[order]': 'DESC',
                        'atts[meta_key]': '',
                        'atts[exclude]': '',
                        'atts[class]': '',
                        'atts[ajax_page]': '',
                        'atts[speed]': '5000',
                        'atts[slides_per_view]': '4',
                        'atts[slides_per_view_tablet]': 'auto',
                        'atts[slides_per_view_mobile]': 'auto',
                        'atts[wrap]': '',
                        'atts[autoplay]': 'no',
                        'atts[center_mode]': 'no',
                        'atts[hide_pagination_control]': '',
                        'atts[hide_prev_next_buttons]': '',
                        'atts[scroll_per_page]': 'yes',
                        'atts[img_size]': 'woocommerce_thumbnail',
                        'atts[force_not_ajax]': 'no',
                        'atts[products_masonry]': '0',
                        'atts[products_different_sizes]': '0',
                        'atts[lazy_loading]': 'yes',
                        'atts[scroll_carousel_init]': 'no',
                        'atts[el_class]': '',
                        'atts[shop_tools]': 'no',
                        'atts[query_post_type]': 'product',
                        'atts[hide_out_of_stock]': 'no',
                        'atts[css]': '',
                        'atts[woodmart_css_id]': '6460f6a67ace8',
                        'atts[ajax_recently_viewed]': 'no',
                        'atts[is_wishlist]': '',
                        'paged': page,
                        'action': 'woodmart_get_products_shortcode',
                        'woo_ajax': '1',
                    }
                    response = self.session.post('https://simplygreentrade.com/wp-admin/admin-ajax.php', data=data)
                    if response.json()['status'] == 'no-more-posts':
                        print(page)
                        break
                    soup = BeautifulSoup(response.json()['items'], 'lxml')
                    cur_product_urls = [x['href'] for x in soup.find_all('a', class_='product-image-link')]
                    for cur_product_url in cur_product_urls:
                        if cur_product_url not in self.product_urls:
                            self.product_urls.append(cur_product_url)

            elif 'product-on-sale' in catalog:
                logging.info('Unable to find products counter')
                page = 0
                while True:
                    page += 1
                    data = {
                        'atts[element_title]': '',
                        'atts[post_type]': 'sale',
                        'atts[layout]': 'grid',
                        'atts[include]': '',
                        'atts[custom_query]': '',
                        'atts[taxonomies]': '',
                        'atts[pagination]': 'infinit',
                        'atts[items_per_page]': '25',
                        'atts[product_hover]': 'standard',
                        'atts[spacing]': '20',
                        'atts[columns]': '5',
                        'atts[columns_tablet]': '3',
                        'atts[columns_mobile]': '2',
                        'atts[sale_countdown]': '0',
                        'atts[stretch_product_desktop]': '0',
                        'atts[stretch_product_tablet]': '0',
                        'atts[stretch_product_mobile]': '0',
                        'atts[stock_progress_bar]': '0',
                        'atts[highlighted_products]': '0',
                        'atts[products_bordered_grid]': '0',
                        'atts[products_bordered_grid_style]': 'outside',
                        'atts[products_with_background]': '0',
                        'atts[products_shadow]': '0',
                        'atts[products_color_scheme]': 'default',
                        'atts[product_quantity]': '0',
                        'atts[grid_gallery]': '',
                        'atts[grid_gallery_control]': '',
                        'atts[grid_gallery_enable_arrows]': '',
                        'atts[offset]': '',
                        'atts[orderby]': 'date',
                        'atts[query_type]': 'OR',
                        'atts[order]': 'DESC',
                        'atts[meta_key]': '',
                        'atts[exclude]': '',
                        'atts[class]': '',
                        'atts[ajax_page]': '',
                        'atts[speed]': '5000',
                        'atts[slides_per_view]': '4',
                        'atts[slides_per_view_tablet]': 'auto',
                        'atts[slides_per_view_mobile]': 'auto',
                        'atts[wrap]': '',
                        'atts[autoplay]': 'no',
                        'atts[center_mode]': 'no',
                        'atts[hide_pagination_control]': '',
                        'atts[hide_prev_next_buttons]': '',
                        'atts[scroll_per_page]': 'yes',
                        'atts[img_size]': 'woocommerce_thumbnail',
                        'atts[force_not_ajax]': 'no',
                        'atts[products_masonry]': '0',
                        'atts[products_different_sizes]': '0',
                        'atts[lazy_loading]': 'yes',
                        'atts[scroll_carousel_init]': 'no',
                        'atts[el_class]': '',
                        'atts[shop_tools]': 'no',
                        'atts[query_post_type]': 'product',
                        'atts[hide_out_of_stock]': 'no',
                        'atts[css]': '',
                        'atts[woodmart_css_id]': '6460f6a67ace8',
                        'atts[ajax_recently_viewed]': 'no',
                        'atts[is_wishlist]': '',
                        'paged': page,
                        'action': 'woodmart_get_products_shortcode',
                        'woo_ajax': '1',
                    }
                    response = self.session.post('https://simplygreentrade.com/wp-admin/admin-ajax.php', data=data)
                    if response.json()['status'] == 'no-more-posts':
                        print(page)
                        break
                    soup = BeautifulSoup(response.json()['items'], 'lxml')
                    cur_product_urls = [x['href'] for x in soup.find_all('a', class_='product-image-link')]
                    for cur_product_url in cur_product_urls:
                        if cur_product_url not in self.product_urls:
                            self.product_urls.append(cur_product_url)
            else:
                pass

    def _parse_details(self, url: str) -> dict | None:
        """

        Parse product details
        :param url: current link
        :return: dict of details | None
        """
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, 'lxml')

        name = soup.find('h1', class_='product_title').text.strip()
        try:
            brand = soup.find('tr',
                              class_='woocommerce-product-attributes-'
                                     'item--attribute_pa_brand').find('td',
                                                                      class_='woocommerce-product-'
                                                                             'attributes-item__value').text.strip()
        except:
            brand = name.split(' ')[0]

        try:
            description = soup.find('div', class_='wd-single-content').extract()
            if description.find('h2'):
                description.find('h2').extract()
            description = description.text.strip()
        except:
            description = None

        breadcrumbs = [x.text.strip() for x in soup.find('nav', class_='woocommerce-breadcrumb').find_all('a', 'breadcrumb-link')[1:]]
        artcile = soup.find('div', class_='sku-single').text.strip()
        price = float(soup.find('p', class_='price').find('span', class_='woocommerce-Price-amount').text.strip().replace('.', '').replace(',', '.').replace('€', ''))
        image = soup.find('figure', class_='woocommerce-product-gallery__image').find('a')['href']

        is_available_text = soup.find('div', class_='detailed-info-stock').find('div', class_='wpb_wrapper').text.strip()
        if is_available_text == 'Available' or is_available_text == 'Limited stock':
            is_available = True
        elif is_available_text == 'Sold out' or is_available_text == 'Out of stock':
            is_available = False
        else:
            logging.error(f'%%%%%%%%%%%%%NEW AVAILABLE STATUS%%%%%%%%%%%%%%%%%%%{is_available_text}')
            return None

        if is_available:
            in_stock = soup.find('div', class_='quantity').find('input', class_='input-text')['max']
        else:
            in_stock = 0

        features = [{x.find('th').text.strip(): x.find('td').text.strip()}
                    for x in soup.find('table', class_='woocommerce-product-attributes').find_all('tr')]

        return {
            'url': url,
            'article': artcile,
            'name': name,
            'brand': brand,
            'image': image,
            'price': price,
            'is_available': is_available,
            'in_stock': in_stock,
            'breadcrumbs': breadcrumbs,
            'description': description,
            'features': features
        }

    def parse_catalog(self):
        self._get_catalog_urls()
        logging.info(f'Total catalogs found: {len(self.catalog_urls)}')
        self._get_product_urls()
        logging.info(f'Total products found: {len(self.product_urls)}')

        all_products = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self._parse_details, product_url) for product_url in self.product_urls]
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
                cur_product = future.result()
                if cur_product:
                    all_products.append(cur_product)

        logging.info(f'Total products parsed {len(all_products)}')
        with open(self.path / 'assets' / 'result.json', 'w+', encoding='utf-8') as file:
            json.dump(all_products, file, indent=4, ensure_ascii=False)
