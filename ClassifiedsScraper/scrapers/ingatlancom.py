from bs4 import BeautifulSoup
import requests
import datetime
import re
import random
import time

from ..scraper_base import ScraperBase
from ..advertisement import Advertisement


class IngatlancomScraper(ScraperBase):
    def __init__(self):
        self.Name = 'ingatlan.com'
        pass

    def Scrape(self, search_string) -> list:
        adList = []

        page_number = 1
        is_done = False
        while is_done is not True:

            url = f'https://ingatlan.com/szukites/{search_string}?page={page_number}'
            # the user-agent header is a must, otherwise we will get a 403
            req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'})

            if not req.ok:
                raise Exception(f'Could not fetch url "{url}" ({req.status_code} - {req.reason})')
                pass

            soup = BeautifulSoup(req.content, 'html.parser')

            products = soup.find_all('div', class_='listing__card')
            print(len(products))

            for product in products:
                productId = product.find('button', class_='listing__hide-undo button--link js-hide-undo')['data-id']
                name = f"{product.find('div', class_='listing__address').text.lstrip()} - {product.find('div', class_='listing__parameter listing__data--area-size').text.lstrip()}, {product.find('div', class_='listing__parameter listing__data--room-count').text.lstrip()}, {product.find('div', class_='listing__parameter listing__data--balcony-size').text.lstrip()}"
                price_text = product.find('div', class_='price').text
                price = re.sub('.M.Ft.*', '', price_text).lstrip()
                category = ''
                auctionType = ''
                link = 'https://ingatlan.com' + product.find('a', class_='listing__thumbnail js-listing-active-area')['href']
                imageUrl = product.find('img', class_='listing__image')['src']
                ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, datetime.datetime.utcnow())
                adList.append(ad)
                #print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
                pass

            pagination = soup.find('div', class_='pagination__page-number').text
            x = re.search(r'(\d*).\/.(\d*) oldal', pagination)
            current_page_no = int(x.group(1))
            max_page_no = int(x.group(2))
            if current_page_no < max_page_no:
                is_done = False
                page_number = current_page_no + 1
                # wait a bit, before fetching the next page
                wait_time = random.randint(4, 11)
                time.sleep(wait_time)
                pass
            else:
                is_done = True
                pass

            pass

        return adList
        pass
    pass

# from bs4 import BeautifulSoup
# import requests
# import datetime
# import re
# import random
# import time

# # adList = []
# search_string = 'elado+lakas+tegla-epitesu-lakas+1-m2erkely-felett+csak-kepes+nem-berleti-jog+xi-ker+43-mFt-ig+45-m2-felett+2-szoba-felett+1-10-felett-emelet'

# page_number = 1
# is_done = False
# while is_done is not True:

#     url = f'https://ingatlan.com/szukites/{search_string}?page={page_number}'
#     # the user-agent header is a must, otherwise we will get a 403
#     req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0'})

#     if not req.ok:
#         raise Exception(f'Could not fetch url "{url}" ({req.status_code} - {req.reason})')
#         pass

#     soup = BeautifulSoup(req.content, 'html.parser')

#     products = soup.find_all('div', class_='listing__card')
#     print(len(products))

#     for product in products:
#         productId = product.find('button', class_='listing__hide-undo button--link js-hide-undo')['data-id']
#         name = f"{product.find('div', class_='listing__address').text} - {product.find('div', class_='listing__parameter listing__data--area-size').text}, {product.find('div', class_='listing__parameter listing__data--room-count').text}, {product.find('div', class_='listing__parameter listing__data--balcony-size').text}"
#         price_text = product.find('div', class_='price').text
#         price = re.sub('.M.Ft.*', '', price_text)
#         category = ''
#         auctionType = ''
#         link = 'https://ingatlan.com' + product.find('a', class_='listing__thumbnail js-listing-active-area')['href']
#         imageUrl = product.find('img', class_='listing__image')['src']
#         # ad = Advertisement(productId, self.Name, name, price, category, auctionType, link, imageUrl, str(datetime.datetime.now()))
#         # adList.append(ad)
#         print(f'({productId}) {name} {price}Ft ({auctionType}, {link}, {imageUrl})')
#         pass

#     pagination = soup.find('div', class_='pagination__page-number').text
#     x = re.search(r'(\d*).\/.(\d*) oldal', pagination)
#     current_page_no = int(x.group(1))
#     max_page_no = int(x.group(2))
#     if current_page_no < max_page_no:
#         is_done = False
#         page_number = current_page_no + 1
#         # wait a bit, before fetching the next page
#         wait_time = random.randint(4, 11)
#         time.sleep(wait_time)
#         pass
#     else:
#         is_done = True
#         pass

#     pass