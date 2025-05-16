import logging
import sys


def setup_logger(level="INFO"):
    logging.basicConfig(
        level=level.upper(),
        format="[%(asctime)s] [%(levelname)s] [%(message)s]",
        handlers=[
            logging.StreamHandler(sys.stdout)
            ]
        )

