import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def main():
    query = "dogum gunu hediyesi" 
    url = f"https://www.ciceksepeti.com/arama?query={query}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print(f"--- [STRUCTURE AUDIT] Ciceksepeti: {query} ---")
        await page.goto(url, wait_until="networkidle")
        
        content = await page.content()
        soup = BeautifulSoup(content, "lxml")
        
        pretty_html = soup.prettify()
        
        with open("ciceksepeti_dom_audit.txt", "w", encoding="utf-8") as f:
            f.write(f"TECHNICAL DOM AUDIT REPORT\n")
            f.write(f"Target: {url}\n")
            f.write("-" * 30 + "\n\n")
            
            f.write("IDENTIFIED SITE LINKS:\n")
            for link in soup.find_all('a', href=True)[:100]: 
                f.write(f"LINK: {link['href']}\n")
                
            f.write("\n" + "="*30 + "\n")
            f.write("BEAUTIFIED SOURCE CODE:\n")
            f.write(pretty_html)

        print("Analiz raporu 'ciceksepeti_dom_audit.txt' olarak kaydedildi.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())