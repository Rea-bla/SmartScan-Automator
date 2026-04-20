from app.scrapers.trendyol import TrendyolScraper
from app.scrapers.hepsiburada import HepsiburadaScraper
from app.scrapers.amazon_tr import AmazonTRScraper
from app.scrapers.n11 import N11Scraper

from app.scrapers.vatanbilgisayar import VatanBilgisayarScraper
from app.scrapers.mediamarkt import MediaMarktScraper
from app.scrapers.teknosa import TeknosaScraper
from app.scrapers.ciceksepeti import CicekSepetiScraper
# Tüm aktif scraper'lar bu listede
ALL_SCRAPERS = [
    TrendyolScraper(),
    HepsiburadaScraper(),
    AmazonTRScraper(),
    N11Scraper(),
    VatanBilgisayarScraper(),
    MediaMarktScraper(),
    TeknosaScraper(),
    CicekSepetiScraper(),
    # Yeni scraper ekledikçe buraya ekle
]