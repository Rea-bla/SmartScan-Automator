import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    url = "https://www.teknosa.com/arama?q=iphone+15"

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

        print("Sayfa yükleniyor, bekleniyor...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000) # Teknosa'nın resimleri/fiyatları yüklemesi için

        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "lxml")

    print("\n=== SAYFA BAŞLIĞI ===")
    print(soup.title.text if soup.title else "YOK")

    print("\n=== 'prd/product/item/card/price' İÇEREN CLASS'LAR ===")
    all_classes = set()
    for tag in soup.find_all(True):
        for c in tag.get("class", []):
            all_classes.add(c)
            
    for c in sorted(all_classes):
        if any(k in c.lower() for k in ["prd", "product", "item", "card", "price", "title"]):
            print(f"  .{c}")

    print("\n=== HTML DOSYAYA KAYDEDİLİYOR ===")
    with open("teknosa_debug.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("teknosa_debug.html kaydedildi!")

asyncio.run(main())