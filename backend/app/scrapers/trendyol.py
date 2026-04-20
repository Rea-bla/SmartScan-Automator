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
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                locale="tr-TR",
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()
            url = f"{self.BASE_URL}/sr?q={query.replace(' ', '+')}"

            try:
                await page.goto(url, timeout=60000, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                await page.evaluate("window.scrollTo(0, 600)")
                await page.wait_for_timeout(2000)

                for _ in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1500)
                
                cards = await page.query_selector_all("[data-testid='image-wrapper-div']")
                print(f"Trendyol: {len(cards)} kart bulundu")

                for card in cards[:20]:
                    try:
                        parent = await card.evaluate_handle(
                            "el => el.closest('.product-card, [class*=product]') || el.parentElement.parentElement"
                        )

                        name_el  = await parent.query_selector("[data-testid='product-card-name'], .product-name, [class*='name']")
                        # Önce price-value dene, yoksa single-price
                        price_el = await parent.query_selector(".price-value")
                        if not price_el:
                            price_el = await parent.query_selector(".single-price")

                        link_el = await parent.query_selector("a")
                        img_el  = await card.query_selector("img")

                        name       = (await name_el.inner_text()).strip() if name_el else ""
                        price_text = (await price_el.inner_text()).strip() if price_el else ""
                        price      = self._parse_price(price_text)
                        href       = await link_el.get_attribute("href") if link_el else ""
                        if href and not href.startswith("http"):
                            href = self.BASE_URL + href
                        img = await img_el.get_attribute("src") if img_el else ""

                        if name and price > 0:
                            results.append(ProductPrice(
                                site=self.SITE_NAME,
                                name=name,
                                price=price,
                                url=href,
                                image_url=img or "",
                            ))
                    except Exception as e:
                        print(f"Kart hatasi: {e}")
                        continue

            except Exception as e:
                print(f"Trendyol hata: {e}")
            finally:
                await browser.close()

        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        # "12.609,03 TL" -> 12609.03
        cleaned = re.sub(r"[^\d,.]", "", text)
        # Nokta binlik ayracı, virgül ondalık
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except ValueError:
            return 0.0