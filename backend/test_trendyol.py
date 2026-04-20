import asyncio
import sys
sys.path.insert(0, ".")

from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        await page.goto("https://www.hepsiburada.com/ara?q=iphone", timeout=60000, wait_until="networkidle")
        await page.wait_for_timeout(5000)
        await page.evaluate("window.scrollTo(0, 600)")
        await page.wait_for_timeout(2000)

        # Tüm class isimlerini tara
        classes = await page.evaluate("""
            () => {
                const all = document.querySelectorAll('[class]')
                const found = new Set()
                all.forEach(d => {
                    if (typeof d.className !== 'string') return
                    d.className.split(' ').forEach(c => {
                        if (c && (
                            c.includes('card') ||
                            c.includes('product') ||
                            c.includes('price') ||
                            c.includes('item') ||
                            c.includes('name')
                        )) {
                            found.add(c)
                        }
                    })
                })
                return [...found].slice(0, 60)
            }
        """)

        print("Hepsiburada class isimleri:")
        for c in classes:
            print(" -", c)

        await page.wait_for_timeout(3000)
        await browser.close()

asyncio.run(test())