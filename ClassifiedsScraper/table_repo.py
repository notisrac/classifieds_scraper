from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from datetime import datetime as DateTime
# import configparser

from .advertisement import Advertisement

class TableRepository(object):
    def __init__(self, connection_string: str, table_name: str):
        self.connection_string = connection_string
        self.table_name = table_name
        # connect to the table storage
        self.table_service = TableService(connection_string=self.connection_string)
        # get the table reference
        if not self.table_service.exists(self.table_name):
            self.table_service.create_table(self.table_name, fail_on_exist=False)
        pass

    def Add(self, ad: Advertisement):
        self.table_service.insert_entity(self.table_name, ad)
        pass

    def Upsert(self, ad: Advertisement):
        ad.lastUpdatedDate: DateTime = DateTime.utcnow()
        self.table_service.insert_or_replace_entity(self.table_name, ad)
        pass

    def Update(self, ad: Advertisement):
        ad.lastUpdatedDate: DateTime = DateTime.utcnow()
        self.table_service.update_entity(self.table_name, ad)
        pass

    def GetIfExists(self, ad: Advertisement):
        try:
            return self.table_service.get_entity(self.table_name, ad.PartitionKey, ad.RowKey)
        except:
            return None
        pass

    def Get(self, id: str, site: str):
        return self.table_service.get_entity(self.table_name, id, site)
        pass

    def Query(self, filter: str):
        return self.table_service.query_entities(self.table_name, filter=filter)
        pass
    pass


# config = configparser.ConfigParser()
# config.read('config.ini')

# # get the table name from the config
# table_name = config["storage"]["table_name"]

# # print(f'{config["storage"]["account_name"]} - {config["storage"]["account_key"]}')

# # connect to the table storage
# table_service = TableService(account_name=config['storage']['account_name'], account_key=config['storage']['account_key'])
# # get the table reference
# if not table_service.exists(table_name):
#     table_service.create_table(table_name)

# # test ad
# datetime_object = datetime.datetime.now()
# ad = Advertisement('123', 'vatera.hu', 'test', '123', 'category/asd', 'fixed', 'https://www.vatera.hu/test-123.html', 'https://p2-ssl.vatera.hu/photos/7d/a5/test_1_300.jpg?v3', str(datetime_object))

# table_service.insert_entity(table_name, ad)