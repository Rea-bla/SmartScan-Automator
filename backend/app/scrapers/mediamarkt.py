import re
from typing import Optional
from bs4 import BeautifulSoup
from app.scrapers.base import AbstractScraper, ProductPrice
from playwright.async_api import async_playwright


class MediaMarktScraper(AbstractScraper):
    SITE_NAME = "MediaMarkt"
    BASE_URL = "https://www.mediamarkt.com.tr"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        url = f"{self.BASE_URL}/tr/search.html?query={query.replace(' ', '+')}"

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
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(5000)
                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")
            cards = soup.select("article[data-test='mms-product-card']")
            print(f"[MediaMarkt] {len(cards)} kart bulundu.")

            for card in cards[:50]:
                try:
                    # Sponsorlu/marketplace ürünleri atla
                    if card.select_one("a[data-test='mms-third-party-provider-link']"):
                        continue

                    name_el  = card.select_one("[data-test='product-title']")
                    price_el = card.select_one("[data-test='mms-price']")
                    link_el  = card.select_one("a[data-test='mms-router-link-product-list-item-link']")
                    img_el   = card.select_one("picture[data-test='product-image'] img")

                    if not (name_el and price_el):
                        continue

                    name  = name_el.get_text(strip=True)
                    price = self._parse_price(price_el.get_text(strip=True))

                    if price <= 0:
                        continue

                    href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + href

                    img = img_el.get("src", "") if img_el else ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME,
                        name=name,
                        price=price,
                        url=href,
                        image_url=img,
                    ))

                except Exception as e:
                    print(f"[MediaMarkt] Item parse hatası: {e}")
                    continue

        except Exception as e:
            print(f"[MediaMarkt] Genel hata: {e}")

        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        # "₺23.899,–" , "₺23.899,00" formatlarını işle
        text = text.replace("₺", "").replace("\xa0", "").strip()

        # Noktalı binlik ayraçlı Türk formatı: X.XXX,XX veya XX.XXX,–
        match = re.search(r"\d{1,3}(?:\.\d{3})+(?:,[\d–-]+)?|\d+(?:,[\d–-]+)?", text)
        if match:
            raw = match.group(0)
            raw = raw.replace(".", "")       # binlik ayracı kaldır
            raw = re.sub(r",.*", "", raw)    # virgülden sonrasını sil
            try:
                val = float(raw)
                if val > 100:
                    return val
            except ValueError:
                pass

        return 0.0