import re
from typing import Optional
from bs4 import BeautifulSoup
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
                # 1. HAMLE: Kendimizi bir iPhone 13 Pro olarak tanıtıyoruz
                iphone_13 = p.devices['iPhone 13 Pro']
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    **iphone_13,
                    locale="tr-TR",
                    timezone_id="Europe/Istanbul"
                )
                
                page = await context.new_page()
                
                # 2. HAMLE: WebDriver izini tamamen siliyoruz
                await page.add_init_script("delete navigator.__proto__.webdriver")

                print(f"[{self.SITE_NAME}] Mobil cihaz taklidiyle sızılıyor...")
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # 3. HAMLE: İnsansı bir kaydırma yapıyoruz
                await page.mouse.wheel(0, 1500)
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")
            
            # Mobil görünümde sınıflar değişebilir, bu yüzden hem .product-item hem .column bakıyoruz
            items = soup.select(".product-item") or soup.select("li.column") or soup.select(".p-card")
            
            print(f"[{self.SITE_NAME}] {len(items)} ürün tespit edildi.")

            for item in items:
                try:
                    # n11 Mobil yapısına uygun seçiciler
                    name_el = item.select_one(".product-item-title") or item.select_one(".productName")
                    price_el = item.select_one(".price") or item.select_one(".basket-price") or item.select_one("ins")
                    
                    if not name_el or not price_el:
                        continue

                    name = " ".join(name_el.get_text(strip=True).split())
                    price = self._parse_price(price_el.get_text(strip=True))
                    
                    if price < 1000: continue # Aksesuarları ele

                    link_el = item.select_one("a")
                    href = link_el.get("href", "") if link_el else ""
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + (href if href.startswith("/") else f"/{href}")

                    img_el = item.select_one("img")
                    img = img_el.get("data-original") or img_el.get("src") or ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME, name=name, price=price, url=href, image_url=img
                    ))
                except:
                    continue

        except Exception as e:
            print(f"[{self.SITE_NAME}] Hata: {e}")

        # Tekilleştirme
        return list({res.url: res for res in results}.values())

    def _parse_price(self, text: str) -> float:
        try:
            cleaned = text.split(',')[0].replace(".", "")
            return float(re.sub(r'[^\d]', '', cleaned))
        except:
            return 0.0

    async def get_price(self, url: str) -> Optional[ProductPrice]: return None