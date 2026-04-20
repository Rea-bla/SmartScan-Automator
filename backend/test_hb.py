# test_hb.py
import asyncio
from curl_cffi import requests
from bs4 import BeautifulSoup

async def test():
    url = "https://www.hepsiburada.com/ara?q=samsung"
    headers = {
        "Accept-Language": "tr-TR,tr;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.hepsiburada.com/",
    }
    async with requests.AsyncSession(impersonate="chrome120") as session:
        response = await session.get(url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select("li[class*='productListContent'], [data-test-id='product-card']")
        print(f"Kart sayısı: {len(cards)}")

        if cards:
            for i, card in enumerate(cards[:3]):
                print(f"\n{'='*50} KART {i+1}")
                # Fiyat içeren tüm elementleri bul
                for el in card.select("[class*='price'], [class*='Price'], [data-test-id*='price']"):
                    text = el.get_text(separator=" ", strip=True)
                    cls = el.get("class")
                    dtid = el.get("data-test-id")
                    if text and any(c.isdigit() for c in text):
                        print(f"  data-test-id={dtid!r} class={cls!r} → {text!r}")

asyncio.run(test())