import datetime
import logging
import os
import json
import jsonpickle

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
# import sendgrid
# from sendgrid.helpers.mail import *

from .table_repo import TableRepository
from .scrapers.vatera import VateraScraper
from .scrapers.hardverapro import HardveraproScraper
from .scrapers.jofogas import JofogasScraper
from .scrapers.ingatlancom import IngatlancomScraper

from .search_settings import SearchSettings
from .search_settings import SearchSetting

from .advertisement import Advertisement

from .advertisement_change import AdvertisementChange
from .advertisement_change import ChangeType

class Scraper(object):
    def __init__(self, search_settings: str, storage_connectionstring: str, table_name: str, email_enabled):
        # the search settings are in a json, so first it needs to be deserialized
        self.search_settings: SearchSettings = jsonpickle.decode(search_settings)
        self.storage_connectionstring: str = storage_connectionstring
        self.table_name: str = table_name
        self.email_enabled = email_enabled

        self.scrapers = []
        self.scrapers.append(VateraScraper())
        self.scrapers.append(HardveraproScraper())
        self.scrapers.append(JofogasScraper())
        self.scrapers.append(IngatlancomScraper())

        self.repo = TableRepository(self.storage_connectionstring, self.table_name)
        pass

    def run(self):
        startDate = datetime.datetime.utcnow()
        found_ads = []

        for setting in self.search_settings.setting_list:
            # the settings allow for disabling a setting, skip those
            if setting.is_enabled:
                # find the scraper in the setting
                for scraper in self.scrapers:
                    if scraper.Name == setting.scraper_name:
                        logging.info(f'Running: {scraper.Name}...')
                        # run the current scraper
                        ads = scraper.Scrape(setting.search_string)
                        # add the advertistments it has found to the repo
                        for ad in ads:
                            change_type = ChangeType.none
                            change = ''
                            logging.info(f'Adding {ad.name}')
                            existing_ad = self.repo.GetIfExists(ad)
                            if existing_ad:
                                if existing_ad.price != ad.price:
                                    change_type = ChangeType.updated
                                    change = f'price: {existing_ad.price} -> {ad.price}'
                                existing_ad.price = ad.price
                                existing_ad.imageUrl = ad.imageUrl
                                existing_ad.link = ad.link
                                self.repo.Update(existing_ad)
                                pass
                            else:
                                change_type = ChangeType.new
                                self.repo.Add(ad)
                                pass
                            pass
                            # if change_type != ChangeType.none:
                            ad_change = AdvertisementChange(ad, change_type, change)
                            found_ads.append(ad_change)
                        # found the scraper, no need to continue the loop
                        break
                        pass
                    pass
                pass
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

    def assemble_email(self, adList: list):
        html = f"""\
        <html>
        <body>
            <h1>Your scraping results!</h1>
            <p>Todays result for your search setting</p>
            <p>
                <table>
        """

        if not adList:
            html = html + "<i>No new ads for today!</i>"
            pass

        for change in adList:
            # if change.change_type = ChangeType.none:
            #     continue
            ad = change.ad
            bg_color = 'FFFFFF'
            if change.change_type == ChangeType.new:
                bg_color = 'a9fc92'
            if change.change_type == ChangeType.updated:
                bg_color = '92bbfc'
            if change.change_type == ChangeType.deleted:
                bg_color = 'fc9292'
            html = html + f"""\
                        <tr style="background-color:#{bg_color}">
                            <td>{ad.site}</td>
                            <td><img src="{ad.imageUrl}" width="100" height="100" /></td>
                            <td>{ad.name}</td>
                            <td>{ad.price}Ft</td>
                            <td><a href="{ad.link}">go to site</a></td>
                            <td>{change.change}</td>
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

    def markItemsAsNotified(self, ad_list: list):
        for change in ad_list:
            ad = change.ad
            ad.IsNotified = True
            self.repo.Update(ad)
            pass
        pass

    def send_notification(self, adList: list):
        if not self.email_enabled:
            logging.info('Email sending is switched off!')
            return

        if not len(adList):
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
