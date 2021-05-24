import datetime
import os
import logging
import json

import azure.functions as func

from ..ClassifiedsScraper.scraper import Scraper

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger at %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())

    searchsettings = req.params.get('searchsettings')
    if not searchsettings:
        searchsettings = os.environ['search_settings']

    scraper = Scraper(searchsettings, os.environ['AzureWebJobsStorage'], os.environ['storage_table_name'], os.environ['email_enabled'])
    found_ads = scraper.run()
    logging.info(f'Found ads: {len(found_ads)}')
    logging.info('Scraper finished ad %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())

    return func.HttpResponse(json.dumps(found_ads, indent=4, sort_keys=True, default=str), status_code=200, mimetype='application/json')
