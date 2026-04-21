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
                # 1. Tarayıcıyı tamamen "Normal Kullanıcı" gibi gösteren flag'lerle açıyoruz
                browser = await p.chromium.launch(
                    headless=True, 
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-web-security",
                        "--allow-running-insecure-content",
                        "--disable-features=IsolateOrigins,site-per-process"
                    ]
                )
                
                # 2. Gerçek bir Windows 11 / Chrome 124 kimliği
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080},
                    ignore_https_errors=True
                )

                page = await context.new_page()

                # 3. Cloudflare'ın 'navigator.webdriver' kontrolünü bozuyoruz
                await page.add_init_script("delete navigator.__proto__.webdriver")

                # 4. Direkt arama sayfasına gitmek yerine önce ana sayfaya "selam verip" geçiyoruz
                print(f"[{self.SITE_NAME}] Kapı çalınıyor...")
                await page.goto(self.BASE_URL, wait_until="networkidle")
                await page.wait_for_timeout(random.randint(2000, 4000))

                # Hediye çerezini enjekte et
                await page.evaluate("""
                    document.cookie = "dynamic-gateway-chosen=extra; path=/; domain=.ciceksepeti.com";
                    localStorage.setItem('dynamic-gateway-chosen', 'extra');
                """)

                # 5. Şimdi aramaya git
                print(f"[{self.SITE_NAME}] İçeri sızılıyor...")
                await page.goto(search_url, wait_until="networkidle")
                
                # Cloudflare challenge'ın geçmesi için ekstra uzun (insansı) bekleme
                await page.wait_for_timeout(8000)

                # Eğer hala koruma sayfasındaysak ekran görüntüsü al
                await page.screenshot(path="cicek_final_deneme.png")
                
                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")
            cards = soup.select("[data-cs-product-box='true']")
            
            print(f"[{self.SITE_NAME}] {len(cards)} kart bulundu.")

            for card in cards[:20]:
                try:
                    name_el = card.select_one("[data-cs-pb-name='true']")
                    price_el = card.select_one("[data-cs-pb-price-text='true']")
                    if not (name_el and price_el): continue

                    name = name_el.get_text(strip=True)
                    price = self._parse_price(price_el.get_text(strip=True))
                    href = card.get("href", "")
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + (href if href.startswith("/") else f"/{href}")

                    img_el = card.select_one("img")
                    img = img_el.get("src") or img_el.get("data-src") or ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME, name=name, price=price, url=href, image_url=img
                    ))
                except: continue

        except Exception as e:
            print(f"[{self.SITE_NAME}] Hata: {e}")

        return results

    def _parse_price(self, text: str) -> float:
        res = re.sub(r'[^\d]', '', text.split(',')[0])
        return float(res) if res else 0.0

    async def get_price(self, url: str) -> Optional[ProductPrice]: return None