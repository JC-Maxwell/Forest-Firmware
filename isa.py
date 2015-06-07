# ============== IMPORT MODULES

# NATIVE

# EXTERNAL

# DEVELOPMENT
from Modules import bill
from Modules import sat

# ============== IMPORT CLASSES

# ============== DEFINE VARIABLES AND CONSTANTS

# VARIABLES

# CONSTANST

# ======================================================== CODE MODULE

# DEFINE FOREST INSTRUCTIONS
instructions = {
	'get_bills_by_date' : bill.get_by_date,
	'get_bills_by_uuid' : bill.get_by_uuid,
	'sat_authentication' : sat.authentication,
	'get_first_bills' : sat.get_first_bills,
	'get_sat_updates' : sat.update,
	'download_from_buffer' : sat.download_from_buffer
}