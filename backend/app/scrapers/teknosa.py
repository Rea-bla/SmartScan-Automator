# GÜNCELLENMİŞ TEKNOSA.PY KODU
import re
from typing import Optional
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from app.scrapers.base import AbstractScraper, ProductPrice

class TeknosaScraper(AbstractScraper):
    SITE_NAME = "Teknosa"
    BASE_URL = "https://www.teknosa.com"

    async def search(self, query: str) -> list[ProductPrice]:
        results = []
        url = f"{self.BASE_URL}/arama?q={query.replace(' ', '+')}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
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
                
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_timeout(4000)
                content = await page.content()
                await browser.close()

            soup = BeautifulSoup(content, "lxml")
            
            # KARTLARI DAHA GENİŞ TUTALIM Kİ LİNKİ KAYBETMEYELİM
            # div.prd-inner yerine direkt dıştaki kapsayıcıyı alıyoruz
            cards = soup.select("ul.prd > li") 
            if not cards:
                cards = soup.select("div.prd-inner")

            print(f"[Teknosa] {len(cards)} kart bulundu.")

            for card in cards[:20]:
                try:
                    name_el  = card.select_one("h3.prd-title")
                    price_el = card.select_one(".prd-prc2") or card.select_one(".prd-prc1") or card.select_one(".prd-prices")
                    
                    # ÇÖZÜM: Linki bulmak için MediaMarkt taktiği (spesifik sınıf veya doğrudan href arama)
                    link_el  = card.select_one("a.prd-link") 
                    if not link_el:
                         # Eğer a.prd-link yoksa, içinde href olan ilk a etiketini bul
                         link_el = card.find("a", href=True)

                    img_el   = card.select_one(".prd-media img") or card.select_one("img")

                    if not (name_el and price_el):
                        continue

                    name_raw = name_el.get_text(separator=" ", strip=True)
                    name = " ".join(name_raw.split())
                    name = re.sub(r'(\d+)\s*(GB|TB)', r'\1 \2', name, flags=re.IGNORECASE)
                    
                    price = self._parse_price(price_el.get_text(strip=True))
                    if price <= 0:
                        continue

                    # MEDIA MARKT STİLİ URL ÇEKME
                    href = link_el["href"] if link_el and "href" in link_el.attrs else ""
                    
                    if href and not href.startswith("http"):
                        href = self.BASE_URL + href

                    img = ""
                    if img_el:
                        img = (
                            img_el.get("data-srcset") 
                            or img_el.get("data-src")
                            or img_el.get("data-lazy-src")
                            or img_el.get("src", "")
                        )
                    if img and "," in img:
                        img = img.split(",")[0].split(" ")[0]
                    if img and ("placeholder" in img or "data:image" in img):
                        img = ""

                    results.append(ProductPrice(
                        site=self.SITE_NAME,
                        name=name,
                        price=price,
                        url=href,
                        image_url=img,
                    ))

                except Exception as e:
                    print(f"[Teknosa] Item parse hatası: {e}")
                    continue

        except Exception as e:
            print(f"[Teknosa] Genel hata: {e}")

        return results

    async def get_price(self, url: str) -> Optional[ProductPrice]:
        return None

    def _parse_price(self, text: str) -> float:
        match = re.search(r"[\d\.]+(?:,[\d]+)?", text)
        if match:
            raw = match.group(0)
            raw = raw.replace(".", "")
            raw = re.sub(r",.*", "", raw)
            try:
                return float(raw)
            except ValueError:
                pass
        numbers = re.findall(r"\d+", text.replace(".", ""))
        for n in numbers:
            val = float(n)
            if val > 100:
                return val
        return 0.0