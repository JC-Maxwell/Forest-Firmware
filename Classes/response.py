# ============== IMPORT MODULES

# NATIVE
import logging

# EXTERNAL
from flask import json
from flask import make_response

# DEVELOPMENT
from Modules import constants as K

# ============== IMPORT CLASSES

# DEFINED ERROR CODES
http_code = {
	'success' : 200,
	'bad_request' : 400,
	'unauthorized' : 401,
	'internal' : 500
}

message = {
	'internal' : "The server encountered a temporary  error and could not complete your request. Please try again later. That's all we know."
}

# ERROR CLASS
class Error():
	http_code = ''
	content = ''

	# CONSTRUCTOR
	def __init__(self, code, content):
		self.http_code = code
		self.content = content

	# METHOD
	def get_json(self):
		error_json = self.content
		return json.dumps(error_json)

	# METHOD
	def get_type(self):
		return K.RESPONSE_TYPE['Error']
	# METHOD
	def get_response(self):
		return make_response(self.get_json(),self.http_code)

# SUCCESS CLASS
class Success():
	http_code = 200
	content = ''

	# CONSTRUCTOR
	def __init__(self, content):
		self.content = content

	# METHOD
	def get_json(self):
		success_json = self.content
		return json.dumps(success_json)

	# METHOD
	def get_type(self):
		return K.RESPONSE_TYPE['Success']

	# METHOD
	def get_response(self):
		return make_response(self.get_json(),self.http_code)