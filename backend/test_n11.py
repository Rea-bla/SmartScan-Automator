import asyncio
from app.scrapers.n11 import N11Scraper

async def main():
    scraper = N11Scraper()
    # iPhone yerine Asus aratarak n11'in standart grid yapısını test ediyoruz
    query = "iphone 15" 
    print(f"n11 Testi Başlıyor: {query}\n")
    results = await scraper.search(query)

    print(f"\nBulunan toplam ürün: {len(results)}")
    for r in results[:10]: # İlk 10 tanesini göster
        print(f"AD    : {r.name}")
        print(f"FİYAT : {r.price} TL")
        print("-" * 30)

if __name__ == "__main__":
    asyncio.run(main())