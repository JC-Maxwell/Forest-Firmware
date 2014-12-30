import logging
from logging.handlers import TimedRotatingFileHandler

def setup_custom_logger(name):
	formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(module)s - %(funcName)s:%(lineno)d - %(message)s','%Y-%m-%d %H:%M:%S')

	# handler = TimedRotatingFileHandler('Logs/app.log', when='midnight')
	handler = logging.StreamHandler()
	handler.setFormatter(formatter)

	logger = logging.getLogger(name)

	# logger.setLevel(logging.INFO)
	logger.setLevel(logging.DEBUG)
	
	logger.addHandler(handler)
	return logger