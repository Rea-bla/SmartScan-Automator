# test_trendyol.py
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="tr-TR",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        await page.goto("https://www.trendyol.com/sr?q=klavye", timeout=60000, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        for _ in range(4):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(1500)

        # Tam HTML yapısını anlamak için ilk kartın class'larını göster
        result = await page.evaluate("""
            () => {
                // Tüm olası selector sayıları
                const counts = {
                    'product-card': document.querySelectorAll('.product-card').length,
                    'class*=product-card': document.querySelectorAll('[class*="product-card"]').length,
                    'p-card-wrppr': document.querySelectorAll('.p-card-wrppr').length,
                    'class*=p-card': document.querySelectorAll('[class*="p-card"]').length,
                }
                
                // İlk kartın TÜM class'larını listele
                const firstCard = document.querySelector('.product-card, [class*="product-card"]')
                const allClasses = firstCard ? firstCard.className : 'BULUNAMADI'
                
                // İlk kartın içindeki tüm elementlerin class'larını listele
                const childClasses = []
                if (firstCard) {
                    firstCard.querySelectorAll('*').forEach(el => {
                        if (el.className && typeof el.className === 'string') {
                            childClasses.push(el.className)
                        }
                    })
                }
                
                return { counts, allClasses, childClasses: childClasses.slice(0, 30) }
            }
        """)
        
        print("Kart sayıları:", result['counts'])
        print("\nİlk kart class:", result['allClasses'])
        print("\nİlk kart child class'ları:")
        for c in result['childClasses']:
            print(f"  {c}")

asyncio.run(test())