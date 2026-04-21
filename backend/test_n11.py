import asyncio
from app.scrapers.n11 import N11Scraper

async def main():
    scraper = N11Scraper()
    query = "iphone 15"
    print(f"Aranıyor: {query}\n")
    results = await scraper.search(query)

    print(f"\nBulunan ürün sayısı: {len(results)}")
    for r in results[:5]:
        print(f"  AD    : {r.name[:70]}")
        print(f"  FİYAT : {r.price} TL")
        print(f"  URL   : {r.url[:70]}")
        print(f"  IMG   : {r.image_url[:70] if r.image_url else '❌ FOTO YOK'}")
        print()

asyncio.run(main())