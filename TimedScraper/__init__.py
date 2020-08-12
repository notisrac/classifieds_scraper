import datetime
import os
import logging

import azure.functions as func

# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail
# import sendgrid
# from sendgrid.helpers.mail import *

from .table_repo import TableRepository
from .scrapers.vatera import VateraScraper
from .scrapers.hardverapro import HardveraproScraper
from .scrapers.jofogas import JofogasScraper

repo: TableRepository = None
scrapers = None
search_term: str = os.environ['search_term']
search_category: str = ''

def init():
    global repo, scrapers

    scrapers = []
    scrapers.append(VateraScraper())
    scrapers.append(HardveraproScraper())
    scrapers.append(JofogasScraper())

    repo = TableRepository(os.environ['AzureWebJobsStorage'], os.environ['storage_table_name'])
    pass

def run():
    global repo, scrapers, search_term, search_category

    startDate = datetime.datetime.utcnow()
    # run all the scrapers
    for scraper in scrapers:
        logging.info(f'Running: {scraper.Name}...')
        # run the current scraper
        ads = scraper.Scrape(search_term, search_category)
        # add the advertistments it has found to the repo
        for ad in ads:
            logging.info(f'Adding {ad.name}')
            repo.Upsert(ad)
            pass
        pass

    # get the newly inserted entities
    new_ads = repo.Query(f"createdDate gt '{startDate}'")
    new_counter = len(new_ads.items)
    if new_counter > 0:
        logging.info(f'New items found: {new_counter}')
        pass
    else:
        logging.info('No new items found')
        pass

    pass

def getNotNotifiedAds():
    ads = repo.Query(f"IsNotified ne true")

    return ads
    pass

def assemble_email(adList):
    global repo, search_term, search_category
    

    html = f"""\
    <html>
    <body>
        <h1>Your scraping results!</h1>
        <p>Todays result for '{search_term}' in '{search_category}'</p>
        <p>
            <table>
    """

    if not adList:
        html = html + "<i>No new ads for today!</i>"
        pass

    for ad in adList:
        html = html + f"""\
                    <tr>
                        <td>{ad.site}</td>
                        <td><img src="{ad.imageUrl}" width="100" height="100" /></td>
                        <td>{ad.name}</td>
                        <td>{ad.price}Ft</td>
                        <td><a href="{ad.link}">go to site</a></td>
                    </tr>
        """
        pass

    html = html + """\
            </table>
        </p>
    </body>
    </html>
    """

    return html
    pass

def markItemsAsNotified(ad_list):
    global repo

    for ad in ad_list:
        ad.IsNotified = True
        repo.Upsert(ad)
        pass
    pass

def send_notification(adList):
    global repo

    if not os.environ['email_enabled']:
        logging.info('Email sending is switched off!')
        return

    # Create the plain-text and HTML version of your message
    html = assemble_email(adList)

    # message = Mail(
    #     from_email=os.environ['email_sender_email'],
    #     to_emails=os.environ['email_receiver_email'],
    #     subject=os.environ['email_subject'],
    #     html_content=html)
    # try:
    #     sg = sendgrid.SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
    #     response = sg.send(message)
    #     logging.info(response.status_code)
    #     logging.info(response.body)
    #     logging.info(response.headers)
    # except Exception as e:
    #     logging.error(str(e))
    #     raise e
    pass

def main(mytimer: func.TimerRequest) -> None:

    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Scraper started at %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
    init()
    run()
    not_notified_ad_list = getNotNotifiedAds()
    if not_notified_ad_list:
        try:
            send_notification(not_notified_ad_list)
            pass
        except Exception as e:
            logging.error('Error while trying to send out the notificaton: ' + str(e))
            pass
        else:
            markItemsAsNotified(not_notified_ad_list)
            pass
    logging.info('Scraper finished ad %s', datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat())
    pass