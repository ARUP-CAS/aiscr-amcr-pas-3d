from . import helper
from django.conf import settings

if(not settings.LOAD_CONSTANTS_FROM_FILE):
	helper.one_time_load_cached_data_doc()
else:
	# To speed up development load the constants from the file
	helper.load_cached_data_from_file()
