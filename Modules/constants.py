# Module for Constants

DOWNLOAD_PATH = '/tmp/Forest/'

BUFFER_PATH = DOWNLOAD_PATH + 'buffer/'

MAX_DOWNLOADS = 100

# FISCAL_STATUS
VALID_STATUS = 'valid'
CANCELED_STATUS = 'canceled'
FISCAL_STATUS = {
	'Vigente' : VALID_STATUS,
	'Cancelado' : CANCELED_STATUS
}

# VOUCHER_EFFECT
INCOME = 'income'
EGRESS = 'egress'
VOUCHER_EFFECT = {
	'Ingreso' : INCOME,
	'Egreso' : EGRESS
}

# RESPONSE
ERROR = 0
SUCCESS = 1
RESPONSE_TYPE = {
	'Success' : SUCCESS,
	'Error' : ERROR
}

# BILLS
RECEIVED_BILL = 1
ISSUED_BILL = 2
BILL_TYPE = {
	'issued' : ISSUED_BILL,
	'received' : RECEIVED_BILL
}

# SEARCH_BILL_BY
DATE = 1
UUID = 2
SERACH_BILLS_BY = {
	'date' : DATE,
	'uuid' : UUID
} 

AUTHORIZED = 'Authorized'
UNAUTHORIZED = 'Unauthorized'
