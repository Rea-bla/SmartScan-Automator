import asyncio
import sys
sys.path.insert(0, ".")

import httpx
from bs4 import BeautifulSoup
import re

async def test():
    url = "https://www.amazon.com.tr/s?k=iphone"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
    }
    async with httpx.AsyncClient(headers=headers, timeout=15, follow_redirects=True) as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select("[data-component-type='s-search-result']")
        print(f"Urun sayisi: {len(items)}")

        for item in items[:3]:
            name_el  = item.select_one("h2 span")
            price_el = item.select_one(".a-price .a-offscreen")
            link_el  = item.select_one("h2 a")

            name       = name_el.get_text(strip=True) if name_el else "ISIM YOK"
            price_text = price_el.get_text(strip=True) if price_el else "FIYAT YOK"
            href       = link_el.get("href", "LINK YOK") if link_el else "LINK YOK"

            print(f"\nUrun: {name[:50]}")
            print(f"  Fiyat ham : {price_text}")
            print(f"  Link      : {href[:80]}")

asyncio.run(test())