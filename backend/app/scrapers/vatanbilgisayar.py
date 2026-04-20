import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import AbstractScraper, ProductPrice
from typing import Optional
import re

class VatanBilgisayarScraper(AbstractScraper):
    SITE_NAME = "Vatan Bilgisayar"
    BASE_URL = "https://www.vatanbilgisayar.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
    }

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        url = f"{self.BASE_URL}/arama/?q={query.replace(' ', '+')}"

        async with httpx.AsyncClient(headers=self.HEADERS, timeout=15, follow_redirects=True) as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.text, "lxml")
                items = soup.select(".product-list__item")

                for item in items[:10]:
                    try:
                        name_el  = item.select_one(".product-list__product-name")
                        price_el = item.select_one(".product-list__price")
                        link_el  = item.select_one("a")
                        img_el   = item.select_one("img")

                        if not (name_el and price_el):
                            continue

                        name  = name_el.get_text(strip=True)
                        price = self._parse_price(price_el.get_text(strip=True))
                        href  = self.BASE_URL + link_el["href"] if link_el else ""
                        img   = img_el.get("data-src") or img_el.get("src", "") if img_el else ""

                        if price > 0:
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=href,
                                image_url=img,
                            ))
                    except Exception:
                        continue
            except Exception as e:
                print(f"Vatan Bilgisayar hata: {e}")

        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        cleaned = re.sub(r"[^\d,.]", "", text)
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0