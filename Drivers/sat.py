# ============== IMPORT MODULES

# NATIVE
from time import sleep
import logging
import time
import sys
import datetime
import calendar as calendarTool 

# EXTERNAL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from pyvirtualdisplay import Display

# DEVELOPMENT
from Modules import log
from Modules import helper
from Modules import constants as K

# ============== IMPORT CLASSES
from Classes.response import Success
from Classes.response import Error
from Classes.response import http_code

# ============== DEFINE VARIABLES, CONSTANTS AND INITIALIZERS

# VARIABLES

# CONSTANST
BUFFER_PATH = K.BUFFER_PATH
WAIT = 20
WAIT_FOR_DOWNLOAD = 1
bill_information = ['actions','uuid','vendor_identifier','vendor_name','client_identifier','client_name','expedition_date','stamp_date','pac','total','type','status','cancelation_date']

# DEFINE LOGS
logger = logging.getLogger('root')

# ======================================================== CODE MODULE

def get_first_bills(**params):
	# Define empty object
	browser = {}

	try:
		# Send to LOGS
		logger.info('Start function in DRIVER')

		# GET PARAMS
		bill_type = params['type']
		identifier = params['credentials']['identifier']
		password = params['credentials']['password']
		year = params['date']['year']
		month = params['date']['month']
		stock = []

		months = [month]

		logger.debug('Date:')
		logger.debug(year)
		logger.debug(months)
		# Get browser
		response = browser_initialize(path=BUFFER_PATH)
		if response.get_type() is K.SUCCESS:
			browser = response.content
			# Get authentication
			response = authentication(browser=browser, identifier=identifier, password=password, method='identifier')
			if response.get_type() is K.SUCCESS and response.content['status'] is K.AUTHORIZED:
				# Search bills and extract CFDI Files
				bills = []
				for month in months:
					response = search_bills(browser=browser, type=bill_type, search_by=K.DATE, date={'year':year,'month':month},stock=stock,first_bills=True)
					if response.get_type() is K.SUCCESS:
						bills = bills + response.content
				
				response = Success(bills)
		logger.info('End of function in DRIVER')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	# CLOSE BROWSER
	browser.quit()
	# SEND RESPONSE
	return response

def get_bills_by_month(**params):
	# Define empty object
	browser = {}

	try:
		# Send to LOGS
		logger.info('Start function in DRIVER')

		# GET PARAMS
		bill_type = params['type']
		identifier = params['credentials']['identifier']
		password = params['credentials']['password']
		year = params['date']['year']
		months = params['date']['months']
		stock = params['stock']

		logger.debug('Date:')
		logger.debug(year)
		logger.debug(months)
		# Get browser
		response = browser_initialize(path=BUFFER_PATH)
		if response.get_type() is K.SUCCESS:
			browser = response.content
			# Get authentication
			response = authentication(browser=browser, identifier=identifier, password=password, method='identifier')
			if response.get_type() is K.SUCCESS and response.content['status'] is K.AUTHORIZED:
				# Search bills and extract CFDI Files
				bills = []
				for month in months:
					response = search_bills(browser=browser, type=bill_type, search_by=K.DATE, date={'year':year,'month':month},stock=stock)
					if response.get_type() is K.SUCCESS:
						bills = bills + response.content
				
				response = Success(bills)
		logger.info('End of function in DRIVER')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	# CLOSE BROWSER
	browser.quit()
	# SEND RESPONSE
	return response



def get_bills_by_uuid(**params):
	browser = {}
	try:
		# Send to LOGS
		logger.info('Start function in DRIVER')

		# GET PARAMS
		bill_type = params['type']
		identifier = params['credentials']['identifier']
		password = params['credentials']['password']
		uuids = params['uuids']
		stock = params['stock']

		bills = []
		# Get browser
		response = browser_initialize(path=BUFFER_PATH)
		if response.get_type() is K.SUCCESS:
			browser = response.content
			# Get authentication
			response = authentication(browser=browser, identifier=identifier, password=password, method='identifier')
			if response.get_type() is K.SUCCESS and response.content['status'] is K.AUTHORIZED:
				# Search bills and extract CFDI Files
				response = search_bills(browser=browser, type=bill_type, search_by=K.UUID, uuids=uuids,stock=stock)
				if response.get_type() is K.SUCCESS: 
					bills = response.content
					response =  Success(bills)
		logger.info('End of function in DRIVER')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	# CLOSE BROWSER
	browser.quit()
	# SEND RESPONSE
	return response
	


def validate_credentials(**params):
	browser = {}
	try:
		logger.debug('Start function in DRIVER')
		# GET PARAMS
		identifier = params['identifier']
		password = params['password']
		# Get browser
		response = browser_initialize()
		if response.get_type() is K.SUCCESS:
			browser = response.content
			# Get authentication
			response = authentication(browser=browser, identifier=identifier, password=password, method='identifier')
		
		logger.debug('End of function in DRIVER')
		
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')

	# Close Browser
	browser.quit()
	# Send response
	return response

def download_bills(**params):
	browser = {}
	try:
		# GET PARAMS
		identifier = params['credentials']['identifier']
		password = params['credentials']['password']
		bills = params['bills']

		response = browser_initialize(path=BUFFER_PATH)
		if response.get_type() is K.SUCCESS:
			browser = response.content
			# Get authentication
			response = authentication(browser=browser, identifier=identifier, password=password, method='identifier')
			if response.get_type() is K.SUCCESS and response.content['status'] is K.AUTHORIZED:
				# Search bills and extract CFDI Files
				response = download_files(browser=browser, bills=bills)
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')

	# Close Browser
	browser.quit()
	# Send response
	return response



# ======================================================== INTERNAL FUNCTIONS

def browser_initialize(**params):	
	# Configure Browser	
	try:
		logger.debug('Start function')
		if 'path' in params:
			
			response = helper.ensure_path(params['path'])
			if response.get_type() is K.SUCCESS:
				# Configurar Firefox para que almacene las facturas en el directorio sin tener que confirmar
				fp = webdriver.FirefoxProfile()
				fp.set_preference("browser.download.folderList",2)
				fp.set_preference("browser.download.manager.showWhenStarting",False)
				fp.set_preference("browser.download.dir", params['path'])
				fp.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/octet-stream")
				# Initialize BROWSER
				logger.debug('Browser Initialize')
				browser = webdriver.Firefox(firefox_profile=fp)
				response = Success(browser)
		else:
			# Initialize BROWSER
			logger.debug('Browser Initialize')
			browser = webdriver.Firefox()
			response = Success(browser)
		logger.debug('End function')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	return response

def authentication(**params):	
	try:
		logger.debug('Start function')
		if params['method'] is 'identifier':
			try:
				# Get browser
				browser = params['browser']
				# Get URL for Login
				browser.get('https://cfdiau.sat.gob.mx/nidp/app/login?id=SATUPCFDiCon&sid=0&option=credential&sid=0')
				# --------------------- FILL AND SEND LOGIN FORM 
				logger.debug('Fill and send Login Form')
				inputRFC = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.NAME, 'Ecom_User_ID')))
				inputRFC.send_keys(params['identifier'])
				inputPassword = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.NAME, 'Ecom_Password')))
				inputPassword.send_keys(params['password'])

				logger.debug('Submitted')
				submit_button = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'submit')))
				submit_button.click()
				# --------------------- END OF FILL AND SEND LOGIN FORM

				# Redirecto to SAT Portal
				logger.debug('Redirect to SAT Portal')
				browser.get('https://portalcfdi.facturaelectronica.sat.gob.mx/')

				# Define Bill Type, if not triggered exception the credentials are correct
				logger.debug('Define Bill Type for verify credentials')
				receivedBillsButton = WebDriverWait(browser,5).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_RdoTipoBusquedaEmisor')))
				receivedBillsButton.click()	

				# Define response
				logger.debug('Authorized')
				response = Success({'status':K.AUTHORIZED})
			except:
				logger.warning('Unauthorized')
				response = Success({'status':K.UNAUTHORIZED})
		elif method is 'fiel':
			pass
		logger.debug('End function')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	return response

def search_bills(**params):
	try:
		logger.debug('Start function')
		# GET PARAMS
		browser = params['browser']
		bill_type = params['type'] 
		search_by = params['search_by']
		stock = params['stock']

		first_bills = False
		if('first_bills' in params):
			first_bills = params['first_bills']

		# --------------------- REDIRECT TO PORTAL
		browser.get('https://portalcfdi.facturaelectronica.sat.gob.mx/')

		# --------------------- DEFINE BILL TYPE
		if bill_type is K.RECEIVED_BILL:
			bills_type_button = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_RdoTipoBusquedaReceptor')))	
		elif bill_type is K.ISSUED_BILL:
			bills_type_button = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_RdoTipoBusquedaEmisor')))
		bills_type_button.click()

		continue_button = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
		continue_button.click()

		# --------------------- DEFINE TYPE OF SEARCH
		logger.debug('Define type search')
		if search_by is K.DATE:
			type_of_search = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_RdoFechas')))
		elif search_by is K.UUID:
			type_of_search = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_RdoFolioFiscal')))
		type_of_search.click()

		if search_by is K.DATE:
			response = search_by_date(browser=browser,type=bill_type,date=params['date'],stock=stock,first_bills=first_bills)
		elif search_by is K.UUID:
			response = search_by_uuid(browser=browser,type=bill_type,uuids=params['uuids'],stock=stock)

		if response.get_type() is K.SUCCESS:
			# Define response
			response = Success(response.content)
		logger.debug('End function')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')
	
	return response

def skip_loading_layer(**params):
	logger.debug('Start function')
	try:
		# GET PARAMS
		browser = params['browser']
		try:
			# --------------------- WAIT FOR LOADING LAYER
			logger.debug('Wa it for loading layer')
			progress_search = WebDriverWait(browser,WAIT).until(EC.visibility_of_element_located((By.ID, 'ctl00_MainContent_UpdateProgress1'))) 

			# --------------------- WAIT FOR LOADING OUT
			logger.debug('Wait for out loading layer')
			progress_search = WebDriverWait(browser,WAIT).until(EC.invisibility_of_element_located((By.ID, 'ctl00_MainContent_UpdateProgress1'))) 
			response = Success(browser)
		except:
			logger.debug('Ingore layers')
			response = Success(browser)
		logger.debug('End function')
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Error: ' + e)
		# Create ERROR
		response = Error(http_code['internal'],'Internal server error')

	return response

def search_by_date(**params):
	try:
		logger.debug('Start function')
		# GET PARAMS
		browser = params['browser']
		bill_type = params['type']
		year = params['date']['year']
		month = params['date']['month']
		stock = params['stock']
		bills = []

		first_bills = False
		if('first_bills' in params):
			first_bills = params['first_bills']
		
		logger.debug('Date:')
		logger.debug(year)
		logger.debug(month)
		# Logic
		if bill_type is K.RECEIVED_BILL:
			
			# --------------------- SELECT YEAR
			select_year = {
				'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]/div[@class='sbHolder']/a[@class='sbToggle']"))),
				'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]/div[@class='sbHolder']/a[@class='sbSelector']")))
			}
			select_year['button'].click()
			time.sleep(2)
			select_year['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]/div[@class='sbHolder']/ul/li/a")))

			for option in select_year['options']:
				if option.text == year:
					option.click()
					break


			# --------------------- SELECT MONTH
			select_month = {
				'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[3]/div[@class='sbHolder']/a[@class='sbToggle']"))),
				'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[3]/div[@class='sbHolder']/a[@class='sbSelector']")))
			}
			select_month['button'].click()
			time.sleep(2)
			select_month['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[3]/div[@class='sbHolder']/ul/li/a")))

			for option in select_month['options']:
				if option.text == month:
					option.click()
					break

		elif bill_type is K.ISSUED_BILL:

			validator_for_calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder']/a[@class='sbToggle']")))			
			init_calendar = WebDriverWait(browser,WAIT).until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_CldFechaInicial2_BtnFecha2'))) 
			init_calendar.click()

			# --------------------- SELECT YEAR
			number_of_click_for_year = (datetime.datetime.now().year - int(year)) * 12

			# Add clicks of month
			number_of_click_for_year = number_of_click_for_year + (datetime.datetime.now().month-1)

			clicks = 1
			while clicks <= number_of_click_for_year:
				calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'datepicker')))
				rows = calendar.find_elements_by_class_name('dpButton') 
				left_row = rows[0]
				left_row.click()
				clicks += 1

			# --------------------- SELECT MONTH
			# Number of Clicks in leftRow
			number_of_click = int(month) - 1
			number_of_day = 1

			clicks = 1
			while clicks <= number_of_click: 
				calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'datepicker')))
				rows = calendar.find_elements_by_class_name('dpButton') 
				# left_row = rows[0]
				# left_row.click()
				right_row = rows[1]
				right_row.click()
				clicks += 1
			
			calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'datepicker')))
			day_buttons = calendar.find_elements_by_class_name('dpTD') 

			counter = 0
			while counter < len(day_buttons):
				if (day_buttons[counter].get_attribute('onclick')):
					first_day = (counter - 1)
					counter = day_buttons
				else:
					counter += 1

			day_buttons[first_day + number_of_day].click()

			validator_for_calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaFinal2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder']/a[@class='sbToggle']")))	
			init_calendar = WebDriverWait(browser,WAIT).until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_CldFechaFinal2_BtnFecha2'))) 
			init_calendar.click()

			number_of_day = calendarTool.monthrange(int(year),int(month))[1]
			
			calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'datepicker')))
			day_buttons = calendar.find_elements_by_class_name('dpTD') 

			counter = 0
			while counter < len(day_buttons):
				if (day_buttons[counter].get_attribute('onclick')):
					first_day = (counter - 2)
					counter = day_buttons
				else:
					counter += 1

			day_buttons[first_day + number_of_day].click()
		
		# --------------------- SEND REQUEST FOR GET BILLS
		search_cfdi = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
		search_cfdi.click()

		# --------------------- HANDLE LOADING LAYER ERROR
		response = skip_loading_layer(browser=browser)
		# --------------------- EXTRACT CFDI FILES
		if response.get_type() is K.SUCCESS:
			browser = response.content 

			try:
				record_limit = WebDriverWait(browser,2).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_PnlLimiteRegistros')))
				# MORE THAN 500
				logger.debug("MORE THAN 500")
				# For each day in month
				number_of_day = calendarTool.monthrange(int(year),int(month))[1]
				if bill_type is K.RECEIVED_BILL:
					for day in range(1,number_of_day + 1):
						if day < 10:
							day = "0" + str(day)
						else:
							day = str(day)
						# --------------------- SELECT DAY
						logger.debug("number of day " + str(day))
						select_day = {
							'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[4]/div[@class='sbHolder']/a[@class='sbToggle']"))),
							'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[4]/div[@class='sbHolder']/a[@class='sbSelector']")))
						}
						select_day['button'].click()
						time.sleep(2)
						select_day['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[4]/div[@class='sbHolder']/ul/li/a")))

						for option in select_day['options']:
							if option.text == day:
								option.click()
								break
						
						# --------------------- SEND REQUEST FOR GET BILLS
						search_cfdi = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
						search_cfdi.click()

						# --------------------- HANDLE LOADING LAYER ERROR
						response = skip_loading_layer(browser=browser)
						# --------------------- EXTRACT CFDI FILES
						if response.get_type() is K.SUCCESS:
							browser = response.content 

							try:
								record_limit = WebDriverWait(browser,2).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_PnlLimiteRegistros')))
								# MORE THAN 500
								logger.debug("MORE THAN 500")

								for hour in range(0,24):
									if hour < 10:
										hour= "0" + str(hour)
									else:
										hour = str(hour)

									# --------------------- SELECT START HOUR
									logger.debug("number of hour " + str(hour))
									select_hour_start = {
										'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
										'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
									}
									select_hour_start['button'].click()
									time.sleep(2)
									select_hour_start['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

									for option in select_hour_start['options']:
										if option.text == hour:
											option.click()
											break

									# --------------------- SELECT START HOUR
									logger.debug("number of hour " + str(hour))
									select_hour_end = {
										'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
										'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
									}
									select_hour_end['button'].click()
									time.sleep(2)
									select_hour_end['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/ul/li/a")))

									for option in select_hour_end['options']:
										if option.text == hour:
											option.click()
											break
									
									# --------------------- SEND REQUEST FOR GET BILLS
									search_cfdi = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
									search_cfdi.click()

									response = cfdi_mining(browser=browser, bills=bills, stock=stock,first_bills=first_bills)
									if response.get_type() is K.SUCCESS:
										# Define response
										logger.debug(str(len(response.content)))
									else:
										logger.debug("No results")

								# --------------------- CLEAR START HOUR
								hour = '00'
								logger.debug("Clear start hour " + str(hour))
								select_hour_start = {
									'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
									'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
								}
								select_hour_start['button'].click()
								time.sleep(2)
								select_hour_start['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[2]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

								for option in select_hour_start['options']:
									if option.text == hour:
										option.click()
										break

								# --------------------- CLEAR END HOUR
								hour = '23'
								logger.debug("Clear end hour " + str(hour))
								select_hour_end = {
									'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
									'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFecha_UpnlSeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
								}
								select_hour_end['button'].click()
								time.sleep(2)
								select_hour_end['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[2]/td[3]//div[@class='sbHolder'][1]/ul/li/a")))

								for option in select_hour_end['options']:
									if option.text == hour:
										option.click()
										break
							except:
								response = cfdi_mining(browser=browser, bills=bills, stock=stock,first_bills=first_bills)
								if response.get_type() is K.SUCCESS:
									# Define response
									logger.debug(str(len(response.content)))
								else:
									logger.debug("No results")
				elif bill_type is K.ISSUED_BILL:
					for day in range(1,number_of_day + 1):
						# Seleccionar en calendario
						validator_for_calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder']/a[@class='sbToggle']")))			
						init_calendar = WebDriverWait(browser,WAIT).until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_CldFechaInicial2_BtnFecha2'))) 
						init_calendar.click()

						calendar = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'datepicker')))
						day_buttons = calendar.find_elements_by_class_name('dpTD') 

						counter = 0
						while counter < len(day_buttons):
							if (day_buttons[counter].get_attribute('onclick')):
								first_day = (counter - 1)
								counter = day_buttons
							else:
								counter += 1

						day_buttons[first_day + day].click()

						# --------------------- SEND REQUEST FOR GET BILLS
						search_cfdi = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
						search_cfdi.click()

						# --------------------- HANDLE LOADING LAYER ERROR
						response = skip_loading_layer(browser=browser)
						# --------------------- EXTRACT CFDI FILES
						if response.get_type() is K.SUCCESS:
							browser = response.content 

							try:
								record_limit = WebDriverWait(browser,2).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_PnlLimiteRegistros')))
								# MORE THAN 500
								logger.debug("MORE THAN 500")

								for hour in range(0,24):
									if hour < 10:
										hour = "0" + str(hour)
									else:
										hour = str(hour)

									# --------------------- SELECT START HOUR
									logger.debug("number of hour " + str(hour))
									select_hour_start = {
										'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
										'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
									}
									select_hour_start['button'].click()
									time.sleep(2)
									select_hour_start['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

									for option in select_hour_start['options']:
										if option.text == hour:
											option.click()
											break

									# --------------------- SELECT START HOUR
									logger.debug("number of hour " + str(hour))
									select_hour_end = {
										'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaFinal2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
										'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaFinal2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
									}
									select_hour_end['button'].click()
									time.sleep(2)
									select_hour_end['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

									for option in select_hour_end['options']:
										if option.text == hour:
											option.click()
											break
									
									# --------------------- SEND REQUEST FOR GET BILLS
									search_cfdi = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_BtnBusqueda')))
									search_cfdi.click()

									# --------------------- HANDLE LOADING LAYER ERROR
									response = skip_loading_layer(browser=browser)

									response = cfdi_mining(browser=browser, bills=bills, stock=stock,first_bills=first_bills)
									if response.get_type() is K.SUCCESS:
										# Define response
										logger.debug(str(len(response.content)))
									else:
										logger.debug("No results")

								# --------------------- CLEAR START HOUR
								logger.debug("Clear start hour")
								hour = '00'
								
								select_hour_start = {
									'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
									'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaInicial2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
								}
								select_hour_start['button'].click()
								time.sleep(2)
								select_hour_start['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

								for option in select_hour_start['options']:
									if option.text == hour:
										option.click()
										break

								# --------------------- CLEAR END HOUR
								hour = '23'
								logger.debug("Clear start hour " + str(hour))
								select_hour_end = {
									'button' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaFinal2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbToggle']"))),
									'input' : WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.XPATH, "//div[@id='ctl00_MainContent_CldFechaFinal2_UpnlSeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/a[@class='sbSelector']")))
								}
								select_hour_end['button'].click()
								time.sleep(2)
								select_hour_end['options'] = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='SeleccionFecha']//tr[1]/td[2]//div[@class='sbHolder'][1]/ul/li/a")))

								for option in select_hour_end['options']:
									if option.text == hour:
										option.click()
										break
							except:
								response = cfdi_mining(browser=browser, bills=bills, stock=stock,first_bills=first_bills)
								if response.get_type() is K.SUCCESS:
									# Define response
									logger.debug(str(len(response.content)))
								else:
									logger.debug("No results")

				response = Success(response.content)
			except:
				# LESS THAN 500
				logger.debug("LESS THAN 500")

				response = cfdi_mining(browser=browser, bills=bills, stock=stock,first_bills=first_bills)
				if response.get_type() is K.SUCCESS:
					response = Success(response.content)

		logger.debug('End function')
	except:
		# Extract Error
		e = str(sys.exc_info()[0]) + " " +  str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	
	return response

def search_by_uuid(**params):
	try:
		logger.debug('Start function')
		# GET PARAMETERS
		browser = params['browser']
		bill_type = params['type']
		uuids = params['uuids']
		stock = params['stock']
		bills = []

		for uuid in uuids:
			# --------------------- TYPE UUID
			inputUUID = WebDriverWait(browser,WAIT).until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_TxtUUID')))
			inputUUID.click()
			inputUUID.send_keys(uuid)

			# --------------------- SEND REQUEST FOR GET BILLS
			searchCFDI = WebDriverWait(browser,WAIT).until(EC.element_to_be_clickable((By.ID, 'ctl00_MainContent_BtnBusqueda')))
			searchCFDI.click()

			# --------------------- HANDLE LOADING LAYER ERROR
			response = skip_loading_layer(browser=browser)
			
			# --------------------- EXTRACT CFDI FILES
			if response.get_type() is K.SUCCESS:
				browser = response.content
				response = cfdi_mining(browser=browser, bills=bills, stock=stock)
				if response.get_type() is K.SUCCESS:
					bills = response.content
			logger.debug('Script')
			browser.execute_script("$('#ctl00_MainContent_TxtUUID').val('')")

		logger.debug('End function')
		response = Success(bills)
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	
	return response

def cfdi_mining(**params):
	try:
		logger.debug('Start function')
		# GET PARAMS
		browser = params['browser']
		bills = params['bills']
		stock = params['stock']

		first_bills = False
		if('first_bills' in params):
			first_bills = params['first_bills']

		# --------------------- GET DIV OF RESULTS
		logger.debug('Get DIV of results')
		div_results = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, 'ctl00_MainContent_PnlResultados')))

		# --------------------- CHECKS FOR RESULTS
		if (div_results.value_of_css_property('display') != 'none'):	
			# --------------------- GET PAGES OF BILLS
			logger.debug('Get pages of bills')
			pages = WebDriverWait(browser,WAIT).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@id='DivPaginas']/*")))
			if(first_bills == True):
				pages = pages[:1]
			# --------------------- FOR EACH PAGE FIND BTNDESCARGA AND CLICK FOR DOWNLOAD BILL
			for page in pages:
				logger.debug('Get rows of page')
				rows = page.find_elements_by_tag_name('tr')
				# --------------------- FOR EACH ROW IN PAGE
				download_buttons = []
				for row in rows:
					cols = row.find_elements_by_tag_name('td')
					uuid = cols[1].find_element_by_tag_name('span').text
					seller = cols[2].find_element_by_tag_name('span').text
					buyer = cols[4].find_element_by_tag_name('span').text
					issued_date = cols[6].find_element_by_tag_name('span').text
					certification_date = cols[7].find_element_by_tag_name('span').text
					voucher_effect = cols[10].find_element_by_tag_name('span').text
					status = cols[11].find_element_by_tag_name('span').text

					
					invoice = {
						'uuid' : str(uuid),
						'seller' : str(seller),
						'buyer' : str(buyer),
						'status' : K.FISCAL_STATUS[status],
						'issued_date' : issued_date,
						'certification_date' : certification_date,
						'voucher_effect' : K.VOUCHER_EFFECT[voucher_effect]
					}

					# if invoice['status'] is K.CANCELED_STATUS:
					# 	invoice['cancelation_date'] = cols[13].find_element_by_tag_name('span').text

					try:
						# --------------------- CHECK IF EXIST FILE
						# if not helper.uuid_is_stored(stock,invoice['uuid']):
							# Comment for Code TEST A1
							# download_button = cols[0].find_element_by_class_name('BtnDescarga').click()
							# download_buttons.append(cols[0].find_element_by_class_name('BtnDescarga'))
							# time.sleep(WAIT_FOR_DOWNLOAD)
						invoice['xml'] = helper.get_link(cols[0].find_element_by_class_name('BtnDescarga').get_attribute('onclick'))
						# else:
						# 	logger.debug('UUID already exist')
					except:
						logger.debug('The file can not be downloaded')

					bills.append(invoice)
					logger.debug(uuid)

				# --------------------- GO TO NEXT PAGE
				logger.debug('Next Page')
				next_page = WebDriverWait(browser,WAIT).until(EC.presence_of_element_located((By.ID, "btnPgSiguiente")))
				next_page.click()

		logger.debug('End function')
		response = Success(bills)
	except:
		# Extract Error
		e = str(sys.exc_info()[0]) + " " + str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')

	return response

def download_files(**params):
	try:
		logger.debug('Start function')
		# Get params
		browser = params['browser']
		bills = params['bills']

		for bill in bills:
			if not helper.uuid_is_stored_in_path(BUFFER_PATH,bill['uuid']) and 'xml' in bill:
				browser.get('https://portalcfdi.facturaelectronica.sat.gob.mx/' + bill['xml'])
				logger.debug('DOWNLOAD ' + bill['uuid'])
				time.sleep(WAIT_FOR_DOWNLOAD)
		response = Success(bills)
	except:
		# Extract Error
		e = str(sys.exc_info()[1])
		# Send to LOGS
		logger.critical('Internal Error ' + e)
		# Define RESPONSE
		response = Error(http_code['internal'],'Internal Server Error')
	logger.debug('End function')
	return response