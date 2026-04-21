import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    async with async_playwright() as p:
        # Tarayıcıyı GÖRÜNÜR (headless=False) açıyoruz
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        
        print("\n--- ETAP 1: n11'e gidiliyor ---")
        await page.goto("https://www.n11.com")
        
        print("\n--- TALİMAT ---")
        print("1. Açılan tarayıcıda arama kutusuna 'iphone 15' veya 'asus' yaz.")
        print("2. Arama sonuçları (ürünler) ekrana tam olarak döküldüğünde...")
        print("3. Buraya (terminale) dön ve ENTER'a bas.")
        
        input("\nÜrünleri gördüysen ENTER'a basarak röntgeni çek...")
        
        # Sen enter'a bastığın an sayfanın o anki canlı HTML'ini alıyoruz
        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        
        # Ürünlerin saklandığı sınıfları bulmak için 'price', 'product', 'item' kelimelerini tarayalım
        print("\n--- CANLI SİTEDEKİ SINIFLAR (SELECTORS) ---")
        found_classes = set()
        for tag in soup.find_all(True):
            cls = tag.get("class", [])
            for c in cls:
                if any(word in c.lower() for word in ["product", "price", "item", "column", "card"]):
                    found_classes.add(c)
        
        for c in sorted(found_classes):
            print(f"  .{c}")

        # HTML'i kaydedelim ki sonra analiz edebilelim
        with open("n11_live_capture.html", "w", encoding="utf-8") as f:
            f.write(content)
            
        print("\n'n11_live_capture.html' kaydedildi. Şimdi bu sınıflara göre kodu güncelleyebiliriz.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())