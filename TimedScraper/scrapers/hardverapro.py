from bs4 import BeautifulSoup
import requests
import datetime

from ..scraper_base import ScraperBase
from ..advertisement import Advertisement


class HardveraproScraper(ScraperBase):
    def __init__(self):
        self.Name = 'hardverapro.hu'
        pass

    def Scrape(self, search_string, search_category):
        adList = []

        url = f'https://hardverapro.hu/aprok/keres.php?stext={search_string}&county=&stcid=&settlement=&stmid=&minprice=&maxprice=&company=&cmpid=&user=&usrid=&selling=1&stext_none='
        req = requests.get(url)

        if not req.ok:
            raise Exception(f'Could not fetch url ({url})')
            pass

        soup = BeautifulSoup(req.content, 'html.parser')

        products = soup.find_all('li', class_='media')
        print(len(products))

        for product in products:
            productId = product['data-uadid']
            nameObject = product.find('div', class_='uad-title').find('a')
            name = nameObject.text
            price = product.find('div', 'uad-price').text
            category = ''
            auctionType = ''
            link = nameObject['href']
            imageUrl = 'https://hardverapro.hu' + product.find('a', class_='uad-image align-self-center').find('img', class_='d-none d-md-block')['src']
            ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, datetime.datetime.utcnow())
            adList.append(ad)
            # print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
            pass
        return adList
        pass
    pass


# from bs4 import BeautifulSoup
# import requests
# import datetime


# # adList = []
# search_string = 'intel'
# url = f'https://hardverapro.hu/aprok/keres.php?stext={search_string}&county=&stcid=&settlement=&stmid=&minprice=&maxprice=&company=&cmpid=&user=&usrid=&selling=1&stext_none='
# req = requests.get(url)

# if not req.ok:
#     raise Exception(f'Could not fetch url ({url})')
#     pass

# soup = BeautifulSoup(req.content, 'html.parser')

# products = soup.find_all('li', class_='media')
# print(len(products))

# for product in products:
#     productId = product['data-uadid']
#     nameObject = product.find('div', class_='uad-title').find('a')
#     name = nameObject.text
#     price = product.find('div', 'uad-price').text
#     category = ''
#     auctionType = ''
#     link = nameObject['href']
#     imageUrl = 'https://hardverapro.hu' + product.find('a', class_='uad-image align-self-center').find('img', class_='d-none d-md-block')['src']
#     # ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, str(datetime.datetime.now()))
#     # adList.append(ad)
#     print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
#     pass

