# ============== IMPORT MODULES

# NATIVE
import os, sys, json

# EXTERNAL
from flask import Flask
from flask import request
from flask import jsonify
from flask import make_response


# DEVELOPMENT
firmware_storage_path = os.path.realpath(__file__).replace("/forest_firmware/main.py", "")
firmware_storage_absolute_path = os.path.abspath(firmware_storage_path)
sys.path.append(firmware_storage_absolute_path)

from forest_firmware.Modules import log
from forest_firmware.isa import instructions as ISA

# ============== IMPORT CLASSES
from forest_firmware.Classes.response import Success
from forest_firmware.Classes.response import Error
from forest_firmware.Classes.response import http_code

# ============== DEFINE VARIABLES, CONSTANTS AND INITIALIZERS

# VARIABLES

# CONSTANST

# DEFINE API CONSTRUCTOR
app = Flask(__name__)

# ======================================================== CODE MODULE

@app.route('/firmware', methods=['POST'])
def api():
	try:
		# Send request to LOGS
		logger.info('Listen request')

		# DESERIALIZE REQUEST 
		request_data = json.loads(request.data)
		
		# VALIDATE REQUEST
		if (('instruction' in request_data) and ('params' in request_data)):
			# GET PARAMS
			instruction = request_data['instruction']
			params = request_data['params']
			# Send to LOGS
			logger.info('Call ' + instruction + ' function')
			# Execute INSTRUCTION
			result = ISA[instruction](params)
			# Define RESPONSE
			response = result.get_response()
		else:
			# Send to LOGS
			logger.info('Bad request')
			# Instance of ERROR 
			error = Error(http_code['bad_request'],'Instruction an Params are required')
			# Define RESPONSE
			response = error.get_response()
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Instance of ERROR
		error = Error(http_code['internal'],'Internal Server Error')
		# Define RESPONSE
		response = error.get_response()
	
	# SEND RESPONSE
	logger.info('End of request')
	return response
	

# MAIN
if __name__ == '__main__':

	# Define LOGGER
	logger = log.setup_custom_logger('root')
	logger.info('Start Forest API Server')

	# Intialize API	
	app.debug = True
	app.run(host='0.0.0.0',threaded=True, port=80)