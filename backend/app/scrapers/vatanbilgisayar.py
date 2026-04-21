import re
from typing import Optional
from bs4 import BeautifulSoup
from app.scrapers.base import AbstractScraper, ProductPrice
from playwright.async_api import async_playwright


class VatanBilgisayarScraper(AbstractScraper):
    SITE_NAME = "Vatan Bilgisayar"
    BASE_URL = "https://www.vatanbilgisayar.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        slug = query.strip().lower().replace(" ", "-")
        url = f"{self.BASE_URL}/arama/{slug}/"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    locale="tr-TR",
                )
                page = await context.new_page()
                await page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)
                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")

            items = [
                el for el in soup.select(".product-list")
                if el.select_one(".product-list__product-name")
            ]

            print(f"[Vatan] {len(items)} ürün bulundu.")

            for item in items[:30]:
                try:
                    name_el  = item.select_one(".product-list__product-name")
                    price_el = item.select_one(".product-list__price")
                    link_el  = item.select_one("a[href]")
                    img_el   = item.select_one("img")

                    if not (name_el and price_el):
                        continue

                    name  = name_el.get_text(strip=True)
                    price = self._parse_price(price_el.get_text(strip=True))

                    if price <= 0:
                        continue

                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + href

                    img = ""
                    if img_el:
                        img = (
                            img_el.get("data-src")
                            or img_el.get("data-lazy-src")
                            or img_el.get("src", "")
                        )

                    results.append(ProductPrice(
                        site=self.SITE_NAME,
                        name=name,
                        price=price,
                        url=href,
                        image_url=img,
                    ))

                except Exception as e:
                    print(f"[Vatan] Item parse hatası: {e}")
                    continue

        except Exception as e:
            print(f"[Vatan] Genel hata: {e}")

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