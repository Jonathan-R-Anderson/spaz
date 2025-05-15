# system/logging.py
import logging
from logging.config import dictConfig
from config import Config

def setup_logging():
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': Config.RTMP_LOG_PATH,
                'formatter': 'default',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file', 'console'],
        },
    })
