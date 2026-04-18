from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice
from typing import Optional
import re

class TrendyolScraper(AbstractScraper):
    SITE_NAME = "Trendyol"
    BASE_URL = "https://www.trendyol.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Bot tespitini azaltmak için user-agent ekle
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            
            url = f"{self.BASE_URL}/sr?q={query}&qt={query}"
            await page.goto(url, timeout=30000)
            
            try:
                await page.wait_for_selector(".p-card-wrppr", timeout=8000)
                cards = await page.query_selector_all(".p-card-wrppr")
                
                for card in cards[:10]:  # İlk 10 ürün
                    try:
                        name_el  = await card.query_selector(".prdct-desc-cntnr-name")
                        price_el = await card.query_selector(".prc-box-dscntd, .prc-box-sllng")
                        link_el  = await card.query_selector("a")
                        img_el   = await card.query_selector("img")

                        if not (name_el and price_el):
                            continue

                        name = (await name_el.inner_text()).strip()
                        price_raw = (await price_el.inner_text()).strip()
                        price = self._parse_price(price_raw)
                        href  = await link_el.get_attribute("href") if link_el else ""
                        img   = await img_el.get_attribute("src") if img_el else ""

                        if price > 0:
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=self.BASE_URL + href,
                                image_url=img,
                            ))
                    except Exception:
                        continue
                        
            except Exception as e:
                print(f"Trendyol scrape hatası: {e}")
            finally:
                await browser.close()
                
        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        # Tekil ürün fiyatı — ileride implemente edilecek
        return None

    def _parse_price(self, text: str) -> float:
        """'1.299,90 TL' -> 1299.90"""
        cleaned = re.sub(r'[^\d,.]', '', text)
        cleaned = cleaned.replace('.', '').replace(',', '.')
        try:
            return float(cleaned)
        except ValueError:
            return 0.0