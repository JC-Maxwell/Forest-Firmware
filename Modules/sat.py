# ============== IMPORT MODULES

# NATIVE
import sys
import math
import datetime

# EXTERNAL
from pymongo import MongoClient
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

def authentication(params):
	try:
		# Send to LOGS
		logger.info('Start function')

		# GET PARAMS
		if 'identifier' in params:
			identifier = params['identifier']
		else:
			identifier = None

		if 'password' in params:
			password = params['password']
		else:
			password = None
			
		if((identifier is not None) and (password is not None)):
			response = sat.validate_credentials(identifier=identifier, password=password)
		else:
			# Instance of ERROR
			response = Error(http_code['bad_request'],'Identifier and Password are required')
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

def update(params):
	try:
		# Get params

		identifier = params['identifier']
		password = params['password']
		year = params['year']
		months = params['months']
		stock = params['uuids']


		logger.debug("===	Start UPDATE function for:")
		logger.debug("		Identifier: " + identifier)

		logger.debug("		UUIDS: " + str(len(stock)))

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

		logger.debug("		Months: " + str(months))

		result =  {
			'new' : [],
			'updated' : []
		}

		total_bills = []

		logger.debug("			START GET LINKS")
		for bill_type in K.BILL_TYPE: 
			logger.debug("			Type of process: " + bill_type)
			for month in months:
					logger.debug("			For Month: " + month)
			response = sat.get_bills_by_month(type=K.BILL_TYPE[bill_type],credentials={'identifier':identifier,'password':password}, date={'year':year,'months':months},stock=stock)
			if response.get_type() is K.SUCCESS and response.content is not K.UNAUTHORIZED:
				bills = response.content
				total_bills = total_bills + bills

		logger.debug("			Total bills before DB: " + str(len(total_bills)))		
		logger.debug("			Get links from DB")

		# Stablish DB connection:
		mongo = MongoClient('mongodb://mikemachine:kikinazul@ds033121-a0.mongolab.com:33121,ds033121-a1.mongolab.com:33121/forest',33121)
		db = mongo['forest']
		db_Buffer = db['Buffer']

		buffers_in_db = db_Buffer.find({"identifier":identifier})
		buffers = helper.get_buffers_from_cursor(buffers_in_db)
		logger.debug("			Buffers: " + str(len(buffers)))

		insert = 0
		for buff in buffers:
			exist = filter(lambda bill: bill['uuid'] == buff['uuid'], total_bills)
			if len(exist) == 0:
				insert = insert + 1
				del buff['_id']
				total_bills.append(buff)

		logger.debug("			Number of insert from db: " + str(insert))


		logger.debug("			END GET LINKS")

		logger.debug("			Extracted bills: " + str(len(total_bills)))
		logger.debug("			Depure array to Mining")

		for invoice in stock:
			for bill in total_bills:
				if invoice['uuid'] == bill['uuid']:
					if invoice['status'] != bill['status']:
						result['updated'].append({"uuid":bill['uuid'],"status":bill['status']})
					total_bills.remove(bill)
					break

		result['new'] = total_bills

		logger.debug("			Bills to updated: " + str(len(result['updated'])))
		logger.debug("			Bills to mining: " + str(len(result['new'])))

				
		logger.debug("			- Remove from Buffer by stock")
		deleted = 0		
		for bill in stock:
			deleted = deleted + 1
			db_Buffer.remove({"uuid":bill['uuid']})
		logger.debug("			- Deleted from stock : " + str(deleted))

		# SECCIONAR EL ARREGLO EN: [[],[],[]] O [[]]
		logger.debug("			Split array of new bills")
		array_of_bills = []
		number_of_sections = int(math.ceil(float(len(result['new']))/K.MAX_DOWNLOADS))
		start = 0
		logger.debug('			Number of sections to download: ' + str(number_of_sections))
		for section in range(1,(number_of_sections + 1)):
			logger.debug('			Section: ' + str(section))
			logger.debug('			Start: ' + str(start))
			logger.debug('			Part of array: ' + str(len(result['new'][start:(section*K.MAX_DOWNLOADS)])))
			array_of_bills.append(result['new'][start:(section*K.MAX_DOWNLOADS)])
			start += K.MAX_DOWNLOADS 
		
		# LUEGO ITERAR SOBRE EL ARREGLO FORMADO
		for index, invoices in enumerate(array_of_bills):
			logger.debug('						Section: ' + str(index + 1))
			response = sat.download_bills(credentials={'identifier':identifier,'password':password},bills=invoices)

		if response.get_type() is K.SUCCESS:
			logger.debug('			Download files: ' + str(len(response.content)))
			for bill in result['new']:
				# Open the xml file for reading
				path_file = K.BUFFER_PATH + bill['uuid'] + '.xml'
				response = helper.read_file(path_file)
				if response.get_type() is K.SUCCESS:
					data = response.content
					if type(data) is str:
						bill['xml'] = data
					else:
						bill['xml'] = ''

		response = Success(result)
				
	except:
		# Extract Error
		e = str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	return response

                                              
def get_first_bills(params):
	try:
		# Get params
		identifier = params['identifier']
		password = params['password']

		# Get current month
		now = datetime.datetime.now()
		
		# Ensure array of Months
		year = now.year
		month = helper.format_month(now.month)

		result =  {
			'new' : [],
			'updated' : []
		}

		total_bills = []

		for bill_type in K.BILL_TYPE: 
			# for month in months:
			response = sat.get_first_bills(type=K.BILL_TYPE[bill_type],credentials={'identifier':identifier,'password':password}, date={'year':year,'month':month})
			if response.get_type() is K.SUCCESS and response.content is not K.UNAUTHORIZED:
				bills = response.content
				total_bills = total_bills + bills
		
		result['new'] = total_bills
		response = sat.download_bills(credentials={'identifier':identifier,'password':password},bills=total_bills)
		if response.get_type() is K.SUCCESS:
			for bill in result['new']:
				# Open the xml file for reading
				path_file = K.BUFFER_PATH + bill['uuid'] + '.xml'
				response = helper.read_file(path_file)
				if response.get_type() is K.SUCCESS:
					data = response.content
					if type(data) is str:
						bill['xml'] = data
					else:
						bill['xml'] = ''		
		response = Success(result)
				
	except:
		# Extract Error
		e = str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	return response

def download_from_buffer(params):
	try:
		# Get params
		identifier = params['identifier']
		password = params['password']
		
		result =  {
			'new' : [],
			'updated' : []
		}

		total_bills = []
	
		logger.debug("			Get links from DB")

		# Stablish DB connection:
		mongo = MongoClient('mongodb://mikemachine:kikinazul@ds033121-a0.mongolab.com:33121,ds033121-a1.mongolab.com:33121/forest',33121)
		db = mongo['forest']
		db_Buffer = db['Buffer']

		buffers_in_db = db_Buffer.find({"identifier":identifier})
		buffers = helper.get_buffers_from_cursor(buffers_in_db)
		logger.debug("			Buffers: " + str(len(buffers)))

		insert = 0
		for buff in buffers:
			exist = filter(lambda bill: bill['uuid'] == buff['uuid'], total_bills)
			if len(exist) == 0:
				insert = insert + 1
				del buff['_id']
				total_bills.append(buff)

		logger.debug("			Number of insert from db: " + str(insert))


		logger.debug("			END GET LINKS")

		logger.debug("			Extracted bills: " + str(len(total_bills)))
		logger.debug("			Depure array to Mining")

		# SE QUITO CAMBIO DE NEW A UPDATED 

		result['new'] = total_bills


		logger.debug("			Bills to updated: " + str(len(result['updated'])))
		logger.debug("			Bills to mining: " + str(len(result['new'])))		
		
		# SECCIONAR EL ARREGLO EN: [[],[],[]] O [[]]
		logger.debug("			Split array of new bills")
		array_of_bills = []
		number_of_sections = int(math.ceil(float(len(result['new']))/K.MAX_DOWNLOADS))
		start = 0
		logger.debug('			Number of sections to download: ' + str(number_of_sections))
		for section in range(1,(number_of_sections + 1)):
			logger.debug('			Section: ' + str(section))
			logger.debug('			Start: ' + str(start))
			logger.debug('			Part of array: ' + str(len(result['new'][start:(section*K.MAX_DOWNLOADS)])))
			array_of_bills.append(result['new'][start:(section*K.MAX_DOWNLOADS)])
			start += K.MAX_DOWNLOADS 
		
		# LUEGO ITERAR SOBRE EL ARREGLO FORMADO
		for invoices in array_of_bills:
			response = sat.download_bills(credentials={'identifier':identifier,'password':password},bills=invoices)

		if response.get_type() is K.SUCCESS:
			logger.debug('			Download files: ' + str(len(response.content)))
			for bill in result['new']:
				# Open the xml file for reading
				path_file = K.BUFFER_PATH + bill['uuid'] + '.xml'
				response = helper.read_file(path_file)
				if response.get_type() is K.SUCCESS:
					data = response.content
					if type(data) is str:
						bill['xml'] = data
					else:
						bill['xml'] = ''

		response = Success(result)
				
	except:
		# Extract Error
		e = str(sys.exc_info()[0]) + ' ' + str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	return response