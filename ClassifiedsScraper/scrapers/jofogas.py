from bs4 import BeautifulSoup
import requests
import datetime

from ..scraper_base import ScraperBase
from ..advertisement import Advertisement


class JofogasScraper(ScraperBase):
    def __init__(self):
        self.Name = 'jofogas.hu'
        pass

    def Scrape(self, search_string, search_category):
        adList = []

        url = f'https://www.jofogas.hu/magyarorszag?q={search_string}'
        req = requests.get(url)

        if not req.ok:
            raise Exception(f'Could not fetch url ({url})')
            pass

        soup = BeautifulSoup(req.content, 'html.parser')

        products = soup.find_all('div',class_="col-xs-12 box listing list-item reListElement")
        # print(len(products))

        for product in products:
            name = product.find('meta', attrs={"itemprop" : "name"})['content']
            link = product.find('meta', attrs={"itemprop" : "url"})['content']
            # the link looks like this: https://www.jofogas.hu/magyarorszag?q=plustek#106789694 - so get the id from the end
            productId = link.split('#', 1)[1]
            category = product.find('meta', attrs={"itemprop" : "category"})['content']
            imageUrl = product.find('meta', attrs={"itemprop" : "image"})['content']
            price = product.find('div', class_='priceBox').find('span', class_='price-value')['content']
            auctionType = ''
            ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, datetime.datetime.utcnow())
            adList.append(ad)
            # print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
            pass

        return adList
        pass
    pass


# import requests
# from bs4 import BeautifulSoup
# page=requests.get("https://www.jofogas.hu/magyarorszag?q=plustek")
# #print(page)
# if page.status_code==200:
#     soup = BeautifulSoup(page.content, 'html.parser')
# soup.prettify()
# addlist = soup.find_all('div',class_="col-xs-12 box listing list-item reListElement")
# for ad in addlist:
#     name = ad.find('meta', attrs={"itemprop" : "name"})['content']
#     link = ad.find('meta', attrs={"itemprop" : "url"})['content']
#     # the link looks like this: https://www.jofogas.hu/magyarorszag?q=plustek#106789694 - so get the id from the end
#     id = link.split('#', 1)[1]
#     category = ad.find('meta', attrs={"itemprop" : "category"})['content']
#     image = ad.find('meta', attrs={"itemprop" : "image"})['content']
#     print(f'{id}, {name}, {link}, {category}, {image}')
#     pass