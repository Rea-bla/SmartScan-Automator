# -*- coding: utf-8 -*-
import httpx
from bs4 import BeautifulSoup
from app.scrapers.base import AbstractScraper, ProductPrice
from typing import Optional
import re


class AmazonTRScraper(AbstractScraper):
    SITE_NAME = "Amazon TR"
    BASE_URL = "https://www.amazon.com.tr"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        search_url = f"{self.BASE_URL}/s?k={query.replace(' ', '+')}"

        async with httpx.AsyncClient(
            headers=self.HEADERS,
            timeout=15,
            follow_redirects=True
        ) as client:
            try:
                response = await client.get(search_url)
                soup = BeautifulSoup(response.text, "lxml")
                items = soup.select("[data-component-type='s-search-result']")
                print(f"[Amazon TR] {len(items)} urun bulundu")

                for item in items[:60]:
                    try:
                        name_el  = item.select_one("h2 span")
                        price_el = item.select_one(".a-price .a-offscreen")
                        img_el   = item.select_one(".s-image")

                        # ASIN'den URL olustur — en guvenilir yontem
                        asin = item.get("data-asin", "")
                        if asin:
                            href = f"{self.BASE_URL}/dp/{asin}"
                        else:
                            # Alternatif: herhangi bir a tag
                            any_link = item.select_one("a.a-link-normal[href]")
                            if any_link:
                                href = any_link.get("href", "")
                                if href.startswith("/"):
                                    href = self.BASE_URL + href
                            else:
                                continue

                        if not name_el or not price_el:
                            continue

                        name  = name_el.get_text(strip=True)
                        price = self._parse_price(price_el.get_text(strip=True))
                        img   = img_el.get("src", "") if img_el else ""

                        if price > 0 and href:
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=href,
                                image_url=img,
                            ))
                    except Exception as e:
                        print(f"[Amazon TR] Kart hatasi: {e}")
                        continue

            except Exception as e:
                print(f"[Amazon TR] Istek hatasi: {e}")

        print(f"[Amazon TR] {len(results)} urun donduruldu")
        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        text = text.replace("\xa0", "").replace("\u00a0", "").strip()
        cleaned = re.sub(r"[^\d,.]", "", text)
        if not cleaned:
            return 0.0
        try:
            if "," in cleaned and "." in cleaned:
                cleaned = cleaned.replace(".", "").replace(",", ".")
            elif "," in cleaned:
                parts = cleaned.split(",")
                if len(parts[-1]) <= 2:
                    cleaned = cleaned.replace(",", ".")
                else:
                    cleaned = cleaned.replace(",", "")
            elif "." in cleaned:
                if len(cleaned.split(".")[-1]) == 3:
                    cleaned = cleaned.replace(".", "")
            result = float(cleaned)
            return result if result >= 1 else 0.0
        except ValueError:
            return 0.0