def setup_logging():
    import logging
    from logging.config import dictConfig
    from config import Config

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {
            'file': {
                'class': 'logging.FileHandler',
                'filename': Config.LOG_FILE_PATH,
                'formatter': 'default',
            },
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['file', 'console']
        }
    })
