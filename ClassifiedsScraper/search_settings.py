class SearchSetting(object):
    def __init__(self, scraper_name: str, is_enabled: bool, search_string: str):
        self.scraper_name = scraper_name
        self.is_enabled = is_enabled
        self.search_string = search_string

class SearchSettings(object):
    def __init__(self, setting_list: list):
        self.version = '1.0'
        self.setting_list = setting_list
