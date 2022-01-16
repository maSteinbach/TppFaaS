import logging
import sys
from .requester import Requester
from .data import create_dataset

info_handler = logging.StreamHandler(sys.stdout)
error_handler = logging.StreamHandler(sys.stderr)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
info_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
info_handler.setLevel(logging.INFO)
error_handler.setLevel(logging.ERROR)
logger = logging.getLogger("sampler")
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.setLevel(logging.INFO)