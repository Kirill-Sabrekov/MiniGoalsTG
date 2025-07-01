import logging
from logging.handlers import RotatingFileHandler

LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)d] %(message)s"
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(),
        RotatingFileHandler("backend.log", maxBytes=5*1024*1024, backupCount=3)
    ]
)
logger = logging.getLogger("backend") 