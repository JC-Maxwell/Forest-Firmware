# ============== IMPORT MODULES

# NATIVE
import datetime
import re
import sys

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

def get_by_date(params):
	try:
		logger.info('Start functions in MODULE')
		# GET PARAMS AND VALIDATE
		bill_type = K.BILL_TYPE[params['type']]

		if 'identifier' in params:
			identifier = params['identifier']
		else:
			identifier = None

		if 'password' in params:
			password = params['password']
		else:
			password = None

		if ('year' in params and
			re.compile('^2[0][1-9][1-9]$').match(params['year']) and
			int(params['year']) in range(2011,datetime.datetime.now().year + 1)):
				year = params['year']
		else:
			year = None

		# Ensure array of Months
		months = []
		if ('months' in params and 
			type(params['months']) is list and 
			len(params['months']) > 0 and
			all(helper.is_integer(month) and int(month) <= 12 for month in params['months'])):
				for month in params['months']:
					months.append(helper.format_month(month))
		else:
			now = datetime.datetime.now()
			for month in range(1,now.month+1):
				months.append(helper.format_month(month))
		
		# LOGIC
		if identifier is not None and password is not None and year is not None:

			for month in months:
				# Driver execution
				PATH_FILES = K.BUFFER_PATH
				bills = {
					"ok" : [],
					"cancel" : [],
					"pending" : []
				}
				response = helper.ensure_path(PATH_FILES)
				if response.get_type() is K.SUCCESS:
					result = sat.get_bills_by_month(type=bill_type,credentials={'identifier':identifier,'password':password}, date={'year':year,'month':month},path=PATH_FILES)
					if result.get_type() is K.SUCCESS:
						for status in result.content:
							for uuid in result.content[status]:
								# Open the xml file for reading
								path_file = PATH_FILES + uuid + '.xml'
								response = helper.read_file(path_file)

								if response.get_type() is K.SUCCESS:
									data = response.content
									if type(data) is str:
										bills[status].append(data)
									else:
										bills['pending'].append(uuid)
						# Define RESPONSE
						response = Success(bills)
		else:
			# Instance of ERROR
			error = Error(http_code['bad_request'],'identifier, password or year are required')
			# Define RESPONSE
			response = error
		logger.info('Start functions in MODULE')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	return response

def get_by_uuid(params):
	try:
		logger.info('Start functions in MODULE')
		# GET PARAMS AND VALIDATE
		bill_type = K.BILL_TYPE[params['type']]

		if 'identifier' in params:
			identifier = params['identifier']
		else:
			identifier = None

		if 'password' in params:
			password = params['password']
		else:
			password = None

		if 'uuids' in params:
			uuids = params['uuids']
		else:
			uuids = []
			result = {'error':'true'}
		
		# Logic
		if ((identifier is not None) and (password is not None) and (len(uuids)>0)):
			PATH_FILES = K.BUFFER_PATH
			bills = {
				"ok" : [],
				"cancel" : [],
				"pending" : []
			}

			response = helper.ensure_path(PATH_FILES)
			if response.get_type() is K.SUCCESS:
				result = sat.get_bills_by_uuid(type=bill_type,credentials={'identifier':identifier,'password':password}, uuids=uuids,path=PATH_FILES)
				if result.get_type() is K.SUCCESS and 'status' not in result.content:
					for status in result.content:
						for uuid in result.content[status]:
							# Open the xml file for reading
							path_file = PATH_FILES + uuid + '.xml'
							response = helper.read_file(path_file)

							if response.get_type() is K.SUCCESS:
								data = response.content
								if type(data) is str:
									bills[status].append(data)
								else:
									bills['pending'].append(uuid)
					# Define RESPONSE
					bills['pending'] = list(set(params['uuids']) - set(result.content['ok']) - set(result.content['cancel']))
					response = Success(bills)

		else:
			result = Error(http_code['bad_request'],'identifier, password or year are required')
		logger.info('Start functions in MODULE')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')

	return response