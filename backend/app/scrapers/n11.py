import re
from typing import Optional
from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice


class N11Scraper(AbstractScraper):
    SITE_NAME = "n11"
    BASE_URL = "https://www.n11.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        url = f"{self.BASE_URL}/arama?q={query.replace(' ', '+')}"

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
                    timezone_id="Europe/Istanbul",
                )
                page = await context.new_page()
                await page.add_init_script(
                    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
                )
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.mouse.wheel(0, 1500)
                await page.wait_for_timeout(3000)

                items = await page.query_selector_all(".product-item")
                print(f"[n11] {len(items)} ürün bulundu.")

                for item in items[:20]:
                    try:
                        # href doğrudan .product-item'ın attribute'unda
                        href = await item.get_attribute("href") or ""

                        name_el  = await item.query_selector(".product-item-title")
                        price_el = await item.query_selector(".basket-price") or \
                                   await item.query_selector(".price")
                        img_el   = await item.query_selector(".product-item-image img")

                        if not (name_el and price_el):
                            continue

                        name       = (await name_el.inner_text()).strip()
                        price_text = (await price_el.inner_text()).strip()
                        price      = self._parse_price(price_text)

                        if price <= 0:
                            continue

                        img = ""
                        if img_el:
                            img = (
                                await img_el.get_attribute("src") or
                                await img_el.get_attribute("data-src") or
                                ""
                            )

                        results.append(ProductPrice(
                            site=self.SITE_NAME,
                            name=name,
                            price=price,
                            url=href,
                            image_url=img,
                        ))

                    except Exception as e:
                        print(f"[n11] Item parse hatası: {e}")
                        continue

                await browser.close()

        except Exception as e:
            print(f"[n11] Genel hata: {e}")

        return list({r.url: r for r in results}.values())

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        # "49.326,85 TLSEPETTE47.526,85 TL" → ilk fiyatı al
        # İlk sayı grubunu yakala: "49.326,85"
        match = re.search(r"[\d\.]+,\d+", text)
        if match:
            raw = match.group(0)          # "49.326,85"
            raw = raw.replace(".", "")    # "49326,85"
            raw = raw.replace(",", ".")   # "49326.85"
            try:
                return float(raw)
            except ValueError:
                pass

        # Fallback: "76.999 TL" gibi virgülsüz format
        match2 = re.search(r"[\d\.]+", text)
        if match2:
            raw = match2.group(0).replace(".", "")
            try:
                val = float(raw)
                if val > 100:
                    return val
            except ValueError:
                pass

        return 0.0