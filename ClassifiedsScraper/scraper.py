import datetime
import logging
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# import sendgrid
# from sendgrid.helpers.mail import *

from .table_repo import TableRepository
from .scrapers.vatera import VateraScraper
from .scrapers.hardverapro import HardveraproScraper
from .scrapers.jofogas import JofogasScraper

class Scraper(object):
    def __init__(self, search_term, storage_connectionstring, table_name, email_enabled):
        self.search_term = search_term
        self.storage_connectionstring = storage_connectionstring
        self.table_name = table_name
        self.search_category = ''
        self.email_enabled = email_enabled

        self.scrapers = []
        self.scrapers.append(VateraScraper())
        self.scrapers.append(HardveraproScraper())
        self.scrapers.append(JofogasScraper())

        self.repo = TableRepository(self.storage_connectionstring, self.table_name)
        pass

    def run(self):
        startDate = datetime.datetime.utcnow()
        found_ads = []
        # run all the scrapers
        for scraper in self.scrapers:
            logging.info(f'Running: {scraper.Name}...')
            # run the current scraper
            ads = scraper.Scrape(self.search_term, self.search_category)
            # add the advertistments it has found to the repo
            for ad in ads:
                logging.info(f'Adding {ad.name}')
                existing_ad = self.repo.GetIfExists(ad)
                if existing_ad:
                    existing_ad.price = ad.price
                    existing_ad.imageUrl = ad.imageUrl
                    existing_ad.link = ad.link
                    self.repo.Update(existing_ad)
                    pass
                else:
                    self.repo.Add(ad)
                    pass
                pass
                found_ads.append(ad)
            pass

        # get the newly inserted entities
        new_ads = self.repo.Query(f"createdDate gt '{startDate}'")
        new_counter = len(new_ads.items)
        if new_counter > 0:
            logging.info(f'New items found: {new_counter}')
            pass
        else:
            logging.info('No new items found')
            pass

        return found_ads
        pass

    def getNotNotifiedAds(self):
        ads = self.repo.Query(f"IsNotified ne true")
        logging.info(f'Items found for notification: {len(ads.items)}')

        return ads
        pass

    def assemble_email(self, adList):
        html = f"""\
        <html>
        <body>
            <h1>Your scraping results!</h1>
            <p>Todays result for '{self.search_term}' in '{self.search_category}'</p>
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

    def markItemsAsNotified(self, ad_list):
        for ad in ad_list:
            ad.IsNotified = True
            self.repo.Upsert(ad)
            pass
        pass

    def send_notification(self, adList):
        if not self.email_enabled:
            logging.info('Email sending is switched off!')
            return

        if not len(adList.items):
            logging.info('Empty notification list!')
            return

        # Create the plain-text and HTML version of your message
        html = self.assemble_email(adList)

        message = Mail(
            from_email=os.environ['email_sender_email'],
            to_emails=os.environ['email_receiver_email'],
            subject=os.environ['email_subject'],
            html_content=html)
        try:
            sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
            response = sg.send(message)
            logging.info(f'Email notificaiton sent (response {response.status_code} - {response.body})')
            # logging.info(response.status_code)
            # logging.info(response.body)
            # logging.info(response.headers)
        except Exception as e:
            logging.error(str(e))
            raise e
        pass

    pass
