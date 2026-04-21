import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    # Boşlukları + ile değiştirerek n11 arama linkini simüle ediyoruz
    url = "https://www.n11.com/arama?q=iphone+15"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("n11 yükleniyor...")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(5000) # Sayfanın tam oturması için 5 sn bekle

        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "lxml")

    print("\n=== SAYFA BAŞLIĞI ===")
    print(soup.title.text if soup.title else "BAŞLIK BULUNAMADI")

    print("\n=== 'product' veya 'column' İÇEREN SINIFLAR ===")
    all_classes = set()
    for tag in soup.find_all(True):
        for c in tag.get("class", []):
            all_classes.add(c)
            
    # Kritik sınıfları filtreleyip ekrana basalım
    for c in sorted(all_classes):
        if any(k in c.lower() for k in ["product", "column", "pro-", "item", "card"]):
            print(f"  .{c}")

    with open("n11_debug.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("\nn11_debug.html kaydedildi!")

asyncio.run(main())