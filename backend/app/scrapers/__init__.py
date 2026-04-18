from app.scrapers.trendyol import TrendyolScraper
from app.scrapers.hepsiburada import HepsiburadaScraper

# Tüm aktif scraper'lar bu listede
ALL_SCRAPERS = [
    TrendyolScraper(),
    HepsiburadaScraper(),
    # Yeni scraper ekledikçe buraya ekle
]