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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                locale="tr-TR",
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()
            url = f"{self.BASE_URL}/sr?q={query.replace(' ', '+')}"

            try:
                await page.goto(url, timeout=40000)
                await page.wait_for_timeout(5500)

                print(f"[Trendyol] Sayfa kaydırılıyor...")
                for _ in range(6):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await page.wait_for_timeout(800)

                cards = await page.query_selector_all("[data-testid='image-wrapper-div']")
                print(f"[Trendyol] {len(cards)} kart bulundu")

                for card in cards[:80]:
                    try:
                        parent = await card.evaluate_handle(
                            "el => el.closest('.product-card, [class*=product]') || el.parentElement.parentElement"
                        )

                        name_el = await parent.query_selector(
                            "[data-testid='product-card-name'], .product-name, [class*='name']"
                        )
                        price_el = await parent.query_selector(".price-value")
                        if not price_el:
                            price_el = await parent.query_selector(".single-price")

                        img_el = await card.query_selector("img")

                        name       = (await name_el.inner_text()).strip() if name_el else ""
                        price_text = (await price_el.inner_text()).strip() if price_el else ""
                        price      = self._parse_price(price_text)
                        img        = await img_el.get_attribute("src") if img_el else ""

                        # ✅ Linki JS ile card'dan yukarı çıkarak al
                        href = await card.evaluate("""el => {
                            let node = el;
                            for (let i = 0; i < 10; i++) {
                                if (!node) break;
                                if (node.tagName === 'A' && node.href) return node.href;
                                // kardeş veya parent içindeki ilk a'yı bul
                                let a = node.querySelector('a[href]');
                                if (a) return a.href;
                                node = node.parentElement;
                            }
                            return '';
                        }""")

                        if not href:
                            # Son çare: parent içindeki ilk linki al
                            link_el = await parent.query_selector("a[href]")
                            href = await link_el.get_attribute("href") if link_el else ""
                            if href:
                                if href.startswith("//"):
                                    href = "https:" + href
                                elif href.startswith("/"):
                                    href = self.BASE_URL + href
                                elif not href.startswith("http"):
                                    href = self.BASE_URL + "/" + href

                        # Regex filtresi
                        if not any(term in name.lower() for term in query.lower().split()):
                            continue

                        if name and price > 0 and href:
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
                print(f"[Trendyol] Hata: {e}")
            finally:
                await browser.close()

        print(f"[Trendyol] {len(results)} ürün döndü")
        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        cleaned = re.sub(r"[^\d,.]", "", text)
        cleaned = cleaned.replace(".", "").replace(",", ".")
        try:
            return float(cleaned)
        except Exception:
            return 0.0