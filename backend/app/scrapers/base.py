from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProductPrice:
    """Bir siteden çekilen tek ürün fiyatı"""
    site: str           # "Trendyol", "Hepsiburada" ...
    name: str           # Ürün adı
    price: float        # Fiyat (TL)
    url: str            # Ürün sayfası linki
    image_url: str = "" # Ürün görseli
    in_stock: bool = True
    original_price: Optional[float] = None  # İndirimli değilse None

class AbstractScraper(ABC):
    SITE_NAME: str = ""

    @abstractmethod
    async def search(self, query: str) -> list[ProductPrice]:
        """Ürün ara, sonuçları döndür"""
        pass

    @abstractmethod  
    async def get_price(self, url: str) -> Optional[ProductPrice]:
        """Tekil ürün sayfasından güncel fiyat çek"""
        pass