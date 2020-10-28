from django.apps import AppConfig
import logging, sys

class CrawlerConfig(AppConfig):
	name = 'crawler'
	verbose_name = "Blockchain Crawler"

	def ready(self):
		if 'runserver' not in sys.argv:
			return True
		# you must import your modules here 
		# to avoid AppRegistryNotReady exception 
		from crawler.tasks import Start
		log = logging.getLogger('console')
		log.warning('Starting crawler task...')
		Start.delay()
		return True
