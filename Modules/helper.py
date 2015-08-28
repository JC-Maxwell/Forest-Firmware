# ============== IMPORT MODULES

# NATIVE
import sys
import os

# EXTERNAL
import logging

# DEVELOPMENT

# ============== IMPORT CLASSES
from forest_firmware.Classes.response import Success
from forest_firmware.Classes.response import Error
from forest_firmware.Classes.response import http_code

# ============== DEFINE VARIABLES, CONSTANTS AND INITIALIZERS

# VARIABLES

# CONSTANST

# DEFINE LOGS
logger = logging.getLogger('root')

# ======================================================== CODE MODULE

# Return true when a string represents a int
def is_integer(s):
    try: 
        int(s)
        response = Success(True)
    except ValueError:
        response = Success(False)

    return response

# Convert a natural number to month in format 01 - 12
def format_month(s):
	try:
		number = int(s)
		if number < 10:
			string = '0' + str(number)
		else:
			string = str(number)
	except:
		string = None

	return string

# Check if uuid is stored
def uuid_is_stored(stock, uuid):
	# result = False
	# if os.path.isfile(path + '/' + uuid + '.xml'):
	# 	result = True
	# return result
	response = False

	for item in stock:
		if str(item['uuid']) == uuid:
			response = True
			break

	return response

def uuid_is_stored_in_path(path, uuid):
	result = False
	if os.path.isfile(path + uuid + '.xml'):
		result = True
	return result

# Verifies the existence of directory, if does not exist create it 
def ensure_path(path):
	try:
		if not os.path.isdir(path):
			os.makedirs(path)
			logger.info('Directory Created: ' + path)
			response = Success(True)
		else:
			response = Success(True)
	except:
		# Extract ERROR
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.error('Problem to Created: ' + path + " " + e)
		# Instance of ERROR
		response = Error(http_code['internal'],e)
	return response

def get_buffers_from_cursor(buffers_cursor):
	buffers = []
	for buffer_in_db in buffers_cursor:# Get a summary of taxpayer due to cursor timeout existance
		buffers.append(buffer_in_db)
	return buffers

# Read File and return Content in String
def read_file(path):
	# Initialize function
	try:
		try:
			# Read FILE
			file = open(path, 'r')
			# Convert to string:
			data = file.read()
			# Close file because dont need it anymore
			file.close()
			# Return string
			response = Success(data)
		except:
			# Cannot read
			response = Success(None)
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	return response

def get_link(string):
	onclick = string.split(" ")
	function = onclick[1].split("'")
	return function[1]