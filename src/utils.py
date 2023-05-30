import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from pathlib import Path
import os
import json


MAX_RETRY_FOR_SESSION = 3
BACK_OFF_FACTOR = 0.3
ERROR_CODES = (500, 501, 502, 503)
PROXY_STATE = 0


def get_session(
        retries: int = MAX_RETRY_FOR_SESSION,
        back_off_factor: int = BACK_OFF_FACTOR,
        status_force_list: list = ERROR_CODES
) -> requests.Session:
    session = requests.Session()
    retry = Retry(total=retries,
                  read=retries,
                  connect=retries,
                  backoff_factor=back_off_factor,
                  status_forcelist=status_force_list,
                  allowed_methods=frozenset(['GET', 'POST']))
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    return session


def create_dir(path: Path) -> None:
    """
    Создает директорию, если ее нет
    :param path: путь
    """
    if not os.path.exists(path):
        os.makedirs(path)


def dump_data(data: list, path: Path, filename: str):
    """
    Сохраняет лист items в json
    """
    create_dir(path)
    with open(path / filename, 'w+', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
