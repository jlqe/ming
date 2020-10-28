from django.db import transaction
import re

LOCK_MODES = (
	'ACCESS SHARE',
	'ROW SHARE',
	'ROW EXCLUSIVE',
	'SHARE UPDATE EXCLUSIVE',
	'SHARE',
	'SHARE ROW EXCLUSIVE',
	'EXCLUSIVE',
	'ACCESS EXCLUSIVE',
)

def require_lock(model, lock):
	"""
	Decorator for PostgreSQL's table-level lock functionality
	
	Example:
		@transaction.commit_on_success
		@require_lock(MyModel, 'ACCESS EXCLUSIVE')
		def myview(request)
			...
	
	PostgreSQL's LOCK Documentation:
	http://www.postgresql.org/docs/8.3/interactive/sql-lock.html
	"""
	def require_lock_decorator(view_func):
		def wrapper(*args, **kwargs):
			if lock not in LOCK_MODES:
				raise ValueError('%s is not a PostgreSQL supported lock mode.')
			from django.db import connection
			cursor = connection.cursor()
			cursor.execute(
				'LOCK TABLE %s IN %s MODE' % (model._meta.db_table, lock)
			)
			return view_func(*args, **kwargs)
		return wrapper
	return require_lock_decorator

def invalid_xml_remove(c):
	#http://stackoverflow.com/questions/1707890/fast-way-to-filter-illegal-xml-unicode-chars-in-python
	illegal_unichrs = [ (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
					(0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
					(0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
					(0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
					(0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
					(0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
					(0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
					(0x10FFFE, 0x10FFFF) ]

	illegal_ranges = ["%s-%s" % (unichr(low), unichr(high)) 
				  for (low, high) in illegal_unichrs 
				  if low < sys.maxunicode]

	illegal_xml_re = re.compile(u'[%s]' % u''.join(illegal_ranges))
	if illegal_xml_re.search(c) is not None:
		#Replace with space
		return ' '
	else:
		return c

