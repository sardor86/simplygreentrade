import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from config import SIMPLY_UTILS_MAX_RETRY_FOR_SESSION, SIMPLY_UTILS_BACK_OFF_FACTOR, SIMPLY_UTILS_ERROR_CODES


def get_session(
        retries: int = SIMPLY_UTILS_MAX_RETRY_FOR_SESSION,
        back_off_factor: int = SIMPLY_UTILS_BACK_OFF_FACTOR,
        status_force_list: list = SIMPLY_UTILS_ERROR_CODES
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
