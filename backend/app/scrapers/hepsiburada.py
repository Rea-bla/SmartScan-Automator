# -*- coding: utf-8 -*-
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
                
                # --- SADECE BURAYI EKLEDİM: 1 ve 2. Sayfayı Gezme Döngüsü ---
                for page_num in range(1, 3): 
                    if len(results) >= 60: 
                        break 
                        
                    paged_url = f"{search_url}&sayfa={page_num}"
                    print(f"[{self.SITE_NAME}] Sayfa {page_num} indiriliyor...")

                    response = await session.get(paged_url, headers=headers, timeout=30)

                    if response.status_code != 200:
                        print(f"[{self.SITE_NAME}] HTTP {response.status_code}")
                        break 

                    soup = BeautifulSoup(response.text, "html.parser")
                    cards = soup.select("li[class*='productListContent'], [data-test-id='product-card']")
                    
                    print(f"[{self.SITE_NAME}] Sayfa {page_num}'de {len(cards)} kart bulundu")
                    
                    if not cards:
                        break 

                    for i, card in enumerate(cards):
                        if len(results) >= 60:
                            break
                        try:
                            # --- BURADAN AŞAĞISI TAMAMEN SENİN ORİJİNAL KODUN ---
                            # --- LINK ---
                            link_el = card.select_one("a[href]")
                            if not link_el:
                                continue
                            href = link_el.get("href", "")
                            if not href or href in seen_urls:
                                continue

                            if href.startswith("/"):
                                full_url = self.BASE_URL + href
                            elif href.startswith("http"):
                                full_url = href
                            else:
                                full_url = self.BASE_URL + "/" + href

                            # --- ISIM ---
                            name = (
                                link_el.get("title")
                                or self._get_text(card, "[data-test-id='product-card-name']")
                                or self._get_text(card, "h3")
                                or link_el.get_text(strip=True)
                            )
                            if not name or len(name) < 3:
                                continue

                            # --- FIYAT ---
                            price = 0.0
                            price_candidates = []

                            for el in card.select("[data-test-id*='price'], [data-test-id*='Price']"):
                                for frac in el.select("[class*='Fraction'], [class*='fraction'], [class*='cent']"):
                                    frac.decompose()
                                t = el.get_text(separator="", strip=True)
                                v = self._parse_price(t)
                                if v > 0:
                                    price_candidates.append(v)

                            if not price_candidates:
                                for selector in [
                                    "[class*='priceValue']",
                                    "[class*='price-value']",
                                    "[class*='finalPrice']",
                                    "[class*='priceInfo']",
                                ]:
                                    for el in card.select(selector):
                                        for frac in el.select("[class*='Fraction'], [class*='fraction']"):
                                            frac.decompose()
                                        t = el.get_text(separator="", strip=True)
                                        v = self._parse_price(t)
                                        if v > 0:
                                            price_candidates.append(v)

                            if price_candidates:
                                valid = [p for p in price_candidates if 10 <= p <= 500000]
                                if valid:
                                    price = min(valid)

                            if price <= 0:
                                continue

                            # --- RESIM ---
                            img_el = card.select_one("img")
                            img_url = ""
                            if img_el:
                                img_url = img_el.get("data-src") or img_el.get("src") or ""

                            seen_urls.add(href)
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=full_url,
                                image_url=img_url,
                            ))

                        except Exception as e:
                            print(f"[{self.SITE_NAME}] Kart hatasi: {e}")
                            continue

        except Exception as e:
            print(f"[{self.SITE_NAME}] Istek hatasi: {e}")

        print(f"[{self.SITE_NAME}] {len(results)} urun donduruldu")
        return results

    def _get_text(self, card, selector: str) -> str:
        el = card.select_one(selector)
        return el.get_text(strip=True) if el else ""

    def _parse_price(self, text: str) -> float:
        text = text.replace("\xa0", "").replace("\u00a0", "").strip()
        cleaned = re.sub(r"[^\d.,]", "", text)
        if not cleaned:
            return 0.0
        return self._convert_to_float(cleaned)

    def _convert_to_float(self, value: str) -> float:
        try:
            if "," in value and "." in value:
                value = value.replace(".", "").replace(",", ".")
            elif "," in value:
                parts = value.split(",")
                if len(parts[-1]) <= 2:
                    value = value.replace(",", ".")
                else:
                    value = value.replace(",", "")
            elif "." in value:
                parts = value.split(".")
                if len(parts[-1]) == 3:
                    value = value.replace(".", "")
            result = float(value)
            if result < 1:
                return 0.0
            return result
        except ValueError:
            return 0.0

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None