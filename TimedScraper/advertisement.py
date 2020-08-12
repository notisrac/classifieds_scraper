from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.cosmosdb.table.models import EntityProperty
from azure.cosmosdb.table.models import EdmType
from datetime import datetime as DateTime

class Advertisement(Entity):
    
    def __init__(self, id: str, site: str, name: str, price: int, category: str, auctionType: str, link: str, imageUrl: str, createdDate: DateTime):
        self.PartitionKey = site
        self.RowKey: str = id
        self.id: str = id
        self.site: str = site
        self.name: str = name
        self.price: int = EntityProperty(EdmType.INT32, price)
        self.category: str = category
        self.auctionType: str = auctionType
        self.link: str = link
        self.imageUrl: str = imageUrl
        self.createdDate: DateTime = EntityProperty(EdmType.DATETIME, createdDate)
        self.lastUpdatedDate: DateTime = EntityProperty(EdmType.DATETIME, createdDate)
        self.IsNotified: bool = EntityProperty(EdmType.BOOLEAN, False)
        pass
    pass