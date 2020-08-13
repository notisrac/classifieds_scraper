import datetime
import os
import logging

import azure.functions as func

from ..ClassifiedsScraper.scraper import Scraper

def main(mytimer: func.TimerRequest) -> None:

    if mytimer.past_due:
        logging.info('The timer is past due!')

    scraper = Scraper(os.environ['search_term'], os.environ['AzureWebJobsStorage'], os.environ['storage_table_name'], os.environ['email_enabled'])

    logging.info('Scraper started at %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
    scraper.run()
    not_notified_ad_list = scraper.getNotNotifiedAds()
    if not_notified_ad_list:
        try:
            scraper.send_notification(not_notified_ad_list)
            pass
        except Exception as e:
            logging.error('Error while trying to send out the notificaton: ' + str(e))
            pass
        else:
            scraper.markItemsAsNotified(not_notified_ad_list)
            pass
    logging.info('Scraper finished ad %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
    pass