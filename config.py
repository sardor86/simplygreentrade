from dataclasses import dataclass
from pathlib import Path
from environs import Env

BASE_DIR = Path(__file__).resolve().parent


SIMPLY_PARSER_BASE_URL = 'https://simplygreentrade.com'
SIMPLY_PARSER_AUTH_URL = 'https://simplygreentrade.com/account/'
SIMPLY_PARSER_ITEMS_PER_PAGE = 24

SIMPLY_PARSER_HEADERS = {
    'authority': 'simplygreentrade.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
              'q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://simplygreentrade.com',
    'referer': 'https://simplygreentrade.com/account/',
    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}


SIMPLY_UTILS_MAX_RETRY_FOR_SESSION = 3
SIMPLY_UTILS_BACK_OFF_FACTOR = 0.3
SIMPLY_UTILS_ERROR_CODES = (500, 501, 502, 503)
SIMPLY_UTILS_PROXY_STATE = 0


@dataclass
class SimplyConfig:
    simply_login: str
    simply_password: str


@dataclass
class WoocommerceConfig:
    wc_key: str
    wc_secret: str
    wc_site: str


@dataclass
class Config:
    simply_config: SimplyConfig
    wc_config: WoocommerceConfig


def load_config(path: str = None) -> Config:
    env = Env()
    env.read_env(path)

    return Config(
        simply_config=SimplyConfig(
            simply_login=env.str('SIMPLY_LOGIN'),
            simply_password=env.str('SIMPLY_PASSWORD')
        ),
        wc_config=WoocommerceConfig(
            wc_key=env.str('CONSUMER_KEY'),
            wc_secret=env.str('CONSUMER_SECRET'),
            wc_site=env.str('WC_SITE')
        )
    )
