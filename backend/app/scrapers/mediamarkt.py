from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice
from typing import Optional
import re

class MediaMarktScraper(AbstractScraper):
    SITE_NAME = "MediaMarkt"
    BASE_URL = "https://www.mediamarkt.com.tr"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })

            url = f"{self.BASE_URL}/tr/search.html?query={query.replace(' ', '+')}"
            try:
                await page.goto(url, timeout=30000)
                await page.wait_for_selector("[data-test='product-list-item']", timeout=8000)
                cards = await page.query_selector_all("[data-test='product-list-item']")

                for card in cards[:10]:
                    try:
                        name_el  = await card.query_selector("[data-test='product-title']")
                        price_el = await card.query_selector("[data-test='product-price']")
                        link_el  = await card.query_selector("a")
                        img_el   = await card.query_selector("img")

                        if not (name_el and price_el):
                            continue

                        name  = (await name_el.inner_text()).strip()
                        price = self._parse_price((await price_el.inner_text()).strip())
                        href  = await link_el.get_attribute("href") if link_el else ""
                        if href and not href.startswith("http"):
                            href = self.BASE_URL + href
                        img = await img_el.get_attribute("src") if img_el else ""

                        if price > 0:
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=href,
                                image_url=img or "",
                            ))
                    except Exception:
                        continue
            except Exception as e:
                print(f"MediaMarkt hata: {e}")
            finally:
                await browser.close()

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