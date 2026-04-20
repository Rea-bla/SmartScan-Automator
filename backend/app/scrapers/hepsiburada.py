from app.scrapers.base import AbstractScraper, ProductPrice
from typing import Optional
import re
from curl_cffi import requests
from bs4 import BeautifulSoup


class HepsiburadaScraper(AbstractScraper):
    SITE_NAME = "Hepsiburada"
    BASE_URL = "https://www.hepsiburada.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        seen_urls = set()
        search_url = f"{self.BASE_URL}/ara?q={query.replace(' ', '%20')}"

        headers = {
            "Accept-Language": "tr-TR,tr;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.hepsiburada.com/",
        }

        try:
            async with requests.AsyncSession(impersonate="chrome120") as session:
                response = await session.get(search_url, headers=headers, timeout=30)

                if response.status_code != 200:
                    print(f"[{self.SITE_NAME}] HTTP {response.status_code}")
                    return results

                soup = BeautifulSoup(response.text, "html.parser")
                cards = soup.select("li[class*='productListContent'], [data-test-id='product-card']")
                print(f"[{self.SITE_NAME}] {len(cards)} kart bulundu")

                for i, card in enumerate(cards):
                    if len(results) >= 20:
                        break

                    try:
                        # --- LINK ---
                        link_el = card.select_one("a[href]")
                        if not link_el:
                            continue
                        href = link_el.get("href", "")
                        if not href or href in seen_urls:
                            continue

                        # --- İSİM ---
                        name = (
                            link_el.get("title")
                            or self._get_text(card, "[data-test-id='product-card-name']")
                            or self._get_text(card, "h3")
                            or link_el.get_text(strip=True)
                        )
                        if not name or len(name) < 3:
                            continue

                        # --- FİYAT ---
                        # data-test-id="final-price-{N}" tam ve doğru fiyatı taşıyor
                        # N kart sırasına göre değişiyor, card index'i ile eşleştir
                        price = 0.0
                        
                        # Yöntem 1: final-price data-test-id (en güvenilir)
                        final_price_el = card.select_one(f"[data-test-id='final-price-{i+1}']")
                        if final_price_el:
                            # Sadece tamsayı kısmını al, kuruş fraction ayrı span'da
                            # "13.830 ,01 TL" → fraction span'ı çıkar, sadece ana değeri al
                            fraction_el = card.select_one("[class*='finalPriceFraction']")
                            if fraction_el:
                                fraction_el.decompose()  # fraction'ı DOM'dan kaldır
                            price_text = final_price_el.get_text(separator="", strip=True)
                            price = self._parse_price(price_text)

                        # Yöntem 2: priceInfo class
                        if price <= 0:
                            price_el = card.select_one("[class*='priceInfo'], [class*='finalPrice']")
                            if price_el:
                                price = self._parse_price(price_el.get_text(separator=" ", strip=True))

                        if price <= 0:
                            continue

                        # --- RESİM ---
                        img_el = card.select_one("img")
                        img_url = ""
                        if img_el:
                            img_url = img_el.get("data-src") or img_el.get("src") or ""

                        seen_urls.add(href)
                        results.append(ProductPrice(
                            site=self.SITE_NAME,
                            name=name,
                            price=price,
                            url=self.BASE_URL + href if href.startswith("/") else href,
                            image_url=img_url,
                        ))

                    except Exception as e:
                        print(f"[{self.SITE_NAME}] Kart hatası: {e}")
                        continue

        except Exception as e:
            print(f"[{self.SITE_NAME}] İstek Hatası: {e}")

        print(f"[{self.SITE_NAME}] {len(results)} ürün döndürüldü")
        return results

    def _get_text(self, card, selector: str) -> str:
        el = card.select_one(selector)
        return el.get_text(strip=True) if el else ""

    def _parse_price(self, text: str) -> float:
        # \xa0 ve unicode boşlukları temizle
        text = text.replace("\xa0", " ").replace("\u00a0", " ")
        cleaned = re.sub(r"[^\d,.]", " ", text).strip()
        matches = re.findall(r'\d+(?:[.,]\d+)*', cleaned)
        if not matches:
            return 0.0
        for match in reversed(matches):
            price = self._convert_to_float(match)
            if price >= 10:
                return price
        return 0.0

    def _convert_to_float(self, value: str) -> float:
        try:
            if "," in value and "." in value:
                value = value.replace(".", "").replace(",", ".")
            elif "," in value:
                value = value.replace(",", ".")
            elif "." in value:
                if len(value.split(".")[-1]) == 3:
                    value = value.replace(".", "")
            return float(value)
        except ValueError:
            return 0.0

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None