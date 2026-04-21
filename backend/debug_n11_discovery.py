import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    # n11 arama linki
    query = "iphone 15"
    url = f"https://www.n11.com/arama?q={query.replace(' ', '+')}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await context.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"n11'e gidiliyor: {url}")
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await page.wait_for_timeout(3000)
        
        content = await page.content()
        await browser.close()

    soup = BeautifulSoup(content, "lxml")

    print("\n=== SAYFA BAŞLIĞI ===")
    print(soup.title.text if soup.title else "YOK")

    print("\n=== TÜM UNIQUE CLASS'LAR (ilk 50) ===")
    all_classes = set()
    for tag in soup.find_all(True):
        for c in tag.get("class", []):
            all_classes.add(c)
    
    for c in sorted(list(all_classes))[:50]:
        print(f"  .{c}")

    print("\n=== 'product' İÇEREN CLASS'LAR ===")
    for c in sorted(all_classes):
        if "product" in c.lower():
            print(f"  .{c}")

    print("\n=== 'price' İÇEREN CLASS'LAR ===")
    for c in sorted(all_classes):
        if "price" in c.lower():
            print(f"  .{c}")

    print("\n=== HTML'İ DOSYAYA KAYDET ===")
    with open("n11_discovery.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("n11_discovery.html dosyasına kaydedildi!")

asyncio.run(main())