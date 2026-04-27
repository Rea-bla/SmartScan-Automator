# -*- coding: utf-8 -*-
import re
from typing import Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice


class AmazonTRScraper(AbstractScraper):
    SITE_NAME = "Amazon TR"
    BASE_URL = "https://www.amazon.com.tr"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        search_url = f"{self.BASE_URL}/s?k={query.replace(' ', '+')}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"]
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    locale="tr-TR",
                    timezone_id="Europe/Istanbul",
                )
                page = await context.new_page()
                await page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )

                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                # Scroll yaparak lazy load ürünleri yükle
                for _ in range(4):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await page.wait_for_timeout(600)

                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")
            items = soup.select("[data-component-type='s-search-result']")
            print(f"[Amazon TR] {len(items)} ürün bulundu")

            for item in items[:20]:
                try:
                    # Sponsorlu reklamları atla
                    if item.select_one(".s-sponsored-label-info-icon"):
                        continue
                    if item.get("data-component-type") == "s-sponsored-result":
                        continue

                    name_el  = item.select_one("h2 span")
                    price_el = item.select_one(".a-price .a-offscreen")
                    img_el   = item.select_one(".s-image")

                    if not (name_el and price_el):
                        continue

                    name  = name_el.get_text(strip=True)
                    price = self._parse_price(price_el.get_text(strip=True))

                    if price <= 0:
                        continue

                    # ASIN'den URL oluştur
                    asin = item.get("data-asin", "")
                    if asin:
                        href = f"{self.BASE_URL}/dp/{asin}"
                    else:
                        link_el = item.select_one("a.a-link-normal[href]")
                        href = link_el["href"] if link_el else ""
                        if href and not href.startswith("http"):
                            href = self.BASE_URL + href

                    if not href:
                        continue

                    img = img_el.get("src", "") if img_el else ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME,
                        name=name,
                        price=price,
                        url=href,
                        image_url=img,
                    ))

                except Exception as e:
                    print(f"[Amazon TR] Kart hatası: {e}")
                    continue

        except Exception as e:
            print(f"[Amazon TR] Genel hata: {e}")

        print(f"[Amazon TR] {len(results)} ürün döndürüldü")
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