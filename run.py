from simply_parser import SimplyGreenTrade
from config import BASE_DIR, load_config
from upload_wc import WooCommerceDriver


def run() -> None:
    config = load_config(BASE_DIR / '.env')

    sgt = SimplyGreenTrade(BASE_DIR, config.simply_config)
    sgt.parse_catalog()

    catalog_url = sgt.catalog_urls

    catalog = [category.split('/')[-2] for category in catalog_url]

    wc_driver = WooCommerceDriver(config.wc_config)
    wc_driver.create_category(catalog)
    wc_driver.add_products(sgt.all_products)


if __name__ == '__main__':
    run()
