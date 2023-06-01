from simply_parser import SimplyGreenTrade
from config import BASE_DIR


def run() -> None:
    sgt = SimplyGreenTrade(BASE_DIR)
    sgt.parse_catalog()


if __name__ == '__main__':
    run()
