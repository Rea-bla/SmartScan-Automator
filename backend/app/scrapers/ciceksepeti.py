import re
import random
from typing import Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice


class CicekSepetiScraper(AbstractScraper):
    SITE_NAME = "Çiçek Sepeti"
    BASE_URL = "https://www.ciceksepeti.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        search_url = f"{self.BASE_URL}/arama?q={query.replace(' ', '+')}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-web-security",
                    ]
                )
                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    viewport={"width": 1920, "height": 1080},
                    locale="tr-TR",
                    timezone_id="Europe/Istanbul",
                    extra_http_headers={
                        "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    }
                )
                page = await context.new_page()

                # Bot tespitini engelle
                await page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr', 'en-US']});
                    window.chrome = { runtime: {} };
                """)

                # Ana sayfaya git
                print(f"[{self.SITE_NAME}] Ana sayfaya gidiliyor...")
                await page.goto(self.BASE_URL, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(random.randint(2000, 3000))

                # Açılış popup'ını geç — "Hediye" veya "Çiçek" butonu
                try:
                    for selector in ["text=Hediye", "text=Devam Et", "button:has-text('Hediye')"]:
                        btn = page.locator(selector).first
                        if await btn.is_visible(timeout=2000):
                            await btn.click()
                            print(f"[{self.SITE_NAME}] Popup geçildi.")
                            await page.wait_for_timeout(1500)
                            break
                except Exception:
                    pass

                # Arama sayfasına git
                print(f"[{self.SITE_NAME}] Arama sayfasına gidiliyor...")
                await page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(random.randint(4000, 5000))

                # İnsan gibi scroll
                await page.mouse.wheel(0, 800)
                await page.wait_for_timeout(1000)
                await page.mouse.wheel(0, 800)
                await page.wait_for_timeout(1000)

                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")

            # Ürün kartlarını bul
            cards = soup.select("[data-cs-product-box='true']")

            if not cards:
                # Cloudflare geçildiyse alternatif selector'lar dene
                cards = (
                    soup.select("[class*='ProductCard']")
                    or soup.select("[class*='product-card']")
                    or soup.select("[class*='product-item']")
                )

            print(f"[{self.SITE_NAME}] {len(cards)} kart bulundu.")

            if not cards:
                all_classes = set()
                for tag in soup.find_all(True):
                    for c in tag.get("class", []):
                        all_classes.add(c)
                relevant = [c for c in sorted(all_classes) if any(
                    k in c.lower() for k in ["product", "card", "item", "price", "result"]
                )]
                print(f"[{self.SITE_NAME}] İlgili class'lar: {relevant[:20]}")
                return results

            for card in cards[:20]:
                try:
                    name_el  = card.select_one("[data-cs-pb-name='true']") or card.select_one("[class*='name']")
                    price_el = card.select_one("[data-cs-pb-price-text='true']") or card.select_one("[class*='price']")

                    if not (name_el and price_el):
                        continue

                    name  = name_el.get_text(strip=True)
                    price = self._parse_price(price_el.get_text(strip=True))

                    if price <= 0:
                        continue

                    href = card.get("href", "")
                    if not href:
                        link_el = card.select_one("a[href]")
                        href = link_el["href"] if link_el else ""
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + href

                    img_el = card.select_one("img")
                    img = ""
                    if img_el:
                        img = img_el.get("src") or img_el.get("data-src") or ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME,
                        name=name,
                        price=price,
                        url=href,
                        image_url=img,
                    ))

                except Exception as e:
                    print(f"[{self.SITE_NAME}] Item parse hatası: {e}")
                    continue

        except Exception as e:
            print(f"[{self.SITE_NAME}] Hata: {e}")

        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        match = re.search(r"[\d\.]+,\d+", text)
        if match:
            raw = match.group(0).replace(".", "").replace(",", ".")
            try:
                return float(raw)
            except ValueError:
                pass
        cleaned = re.sub(r"[^\d]", "", text.split(",")[0])
        return float(cleaned) if cleaned else 0.0