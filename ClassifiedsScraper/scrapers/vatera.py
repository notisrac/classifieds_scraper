from bs4 import BeautifulSoup
import requests
import datetime

from ..scraper_base import ScraperBase
from ..advertisement import Advertisement


class VateraScraper(ScraperBase):
    def __init__(self):
        self.Name = 'vatera.hu'
        pass

    def Scrape(self, search_string) -> list:
        adList = []

        url = f'https://www.vatera.hu/listings/index.php?{search_string}'
        req = requests.get(url)

        if not req.ok:
            raise Exception(f'Could not fetch url ({url})')
            pass

        soup = BeautifulSoup(req.content, 'html.parser')

        products = soup.find_all('div', class_='gtm-impression prod')
        # print(len(products))

        for product in products:
            productId = product['data-gtm-id']
            name = product['data-gtm-name']
            price = product['data-gtm-price']
            category = product['data-gtm-category']
            auctionType = product['data-gtm-auction-type']
            link = product.find('a', class_='product_link')['href']
            imageUrl = product.find('div', class_='pic-holder').find('div', class_='picbox').img['data-original']
            ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, datetime.datetime.utcnow())
            adList.append(ad)
            # print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
            pass

        return adList
        pass
    pass