from django import template
import time

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def epoch_timestamp_to_datetime(epoch):

	if(epoch == 0 or epoch is None or epoch == '' or epoch == -1):
		return 'N/A'

	return time.strftime('%Y-%m-%d %H:%M', time.localtime(epoch))
