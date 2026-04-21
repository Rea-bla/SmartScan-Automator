import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    url = "https://www.ciceksepeti.com/arama?q=iphone+15"

    async with async_playwright() as p:
        # headless=False yaptık ki tarayıcıyı ekranda görebilelim!
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
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

        print("Çiçek Sepeti tarayıcıda açılıyor...")
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # BİZİM İÇİN EN ÖNEMLİ SATIR: 
        # Tarayıcı açıldığında eğer karşına CAPTCHA veya "Ben robot değilim" çıkarsa, 
        # onu elinle çöz. Sonra terminale gelip Enter'a bas.
        input("\nTarayıcıdaki duruma bak. Ürünler yüklendiyse terminalde ENTER'a bas...")

        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "lxml")

    print("\n=== 'product/item/card/price' İÇEREN CLASS'LAR ===")
    all_classes = set()
    for tag in soup.find_all(True):
        for c in tag.get("class", []):
            all_classes.add(c)
            
    for c in sorted(all_classes):
        if any(k in c.lower() for k in ["product", "item", "card", "price", "title"]):
            print(f"  .{c}")

    with open("cicek_debug.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("cicek_debug.html kaydedildi!")

asyncio.run(main())