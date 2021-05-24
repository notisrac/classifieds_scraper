# Classifieds Scraper
An automated function for scraping advertistments on different classifieds sites, looking for a serach word.

 - Based on Azure Functions
 - Data is stored in Azure Storage tables
 - Plug-in based scrapers for different sites

## Scraping modules
Currently scraper modules are available for the following sites:
 - jofogas.hu
 - vatera.hu
 - hardverapro.hu
 - ingatlan.com

To create a plug-in, you need to inherit from ```scraper_base.py```:
```python
from bs4 import BeautifulSoup
import requests

from ..scraper_base import ScraperBase
from ..advertisement import Advertisement


class SampleSiteScraper(ScraperBase):
    def __init__(self):
        self.Name = 'sample_site'
        pass

    def Scrape(self, search_string) -> list:
        adList = []

        url = f'https://www.samplesite.com?{search_string}'
        req = requests.get(url)

        if not req.ok:
            raise Exception(f'Could not fetch url ({url})')
            pass

        # do scraping
        # create new Advertistement object, with scraped data
        # add data to adList

        return adList
        pass
    pass
```