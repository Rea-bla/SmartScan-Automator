import asyncio
from app.scrapers.vatanbilgisayar import VatanBilgisayarScraper

async def main():
    scraper = VatanBilgisayarScraper()
    results = await scraper.search("laptop")
    print(f"Toplam: {len(results)}")
    for r in results[:5]:
        print(f"  AD    : {r.name[:60]}")
        print(f"  FİYAT : {r.price} TL")
        print(f"  URL   : {r.url[:70]}")
        print(f"  IMG   : {r.image_url[:80] if r.image_url else '❌ FOTO YOK'}")
        print()

asyncio.run(main())