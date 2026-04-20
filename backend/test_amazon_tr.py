# test_amazon.py - tamamını bununla değiştir
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
        )
        page = await context.new_page()
        await page.goto("https://www.amazon.com.tr/s?k=samsung", timeout=60000, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        cards = await page.query_selector_all("div[data-component-type='s-search-result']")
        print(f"Kart sayısı: {len(cards)}")

        if cards:
            card = cards[0]
            
            # .a-offscreen elementlerini bul ve text_content ile inner_text farkını göster
            offscreens = await card.query_selector_all(".a-offscreen")
            print(f"\na-offscreen element sayısı: {len(offscreens)}")
            for i, el in enumerate(offscreens):
                tc = await el.text_content()
                it = await el.inner_text()
                print(f"  [{i}] text_content={tc!r}  inner_text={it!r}")

            # JavaScript ile direkt oku
            print("\n--- JavaScript ile fiyat okuma ---")
            js_result = await page.evaluate("""(card) => {
                const els = card.querySelectorAll('.a-offscreen');
                return Array.from(els).map(el => el.textContent);
            }""", card)
            print(f"JS sonucu: {js_result}")

        await browser.close()

asyncio.run(test())