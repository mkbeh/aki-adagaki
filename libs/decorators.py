import logging


# Func which log func success result.
def log(func):
    def wrapper(*args, **kwargs):
        if not func(*args, **kwargs):
            logging.basicConfig(filename='aki-adagaki.log', level=logging.INFO,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.info('Success status: DONE')

    return wrapper


# Func which log func success result.
def write_log(func):
    def wrapper(*args, **kwargs):
        if func(*args, **kwargs) is None:
            logging.basicConfig(filename='aki-adagaki.log', level=logging.INFO,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            logging.info('Success write data.')

    return wrapper
