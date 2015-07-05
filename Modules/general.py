# ============== IMPORT MODULES

# NATIVE

# EXTERNAL
import logging

# DEVELOPMENT
from Drivers import sat
from Modules import helper
from Modules import constants as K

# ============== IMPORT CLASSES
from Classes.response import Success
from Classes.response import Error
from Classes.response import http_code

# ============== DEFINE VARIABLES, CONSTANTS AND INITIALIZERS

# VARIABLES

# CONSTANST

# DEFINE LOGS
logger = logging.getLogger('root')

# ======================================================== CODE MODULE

def get_status(params):
	try:
		# Send to LOGS
		logger.info('Start function')

		# GET PARAMS
		response = Success(True) 
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')

	# SEND RESPONSE
	logger.info('End of function')
	return response