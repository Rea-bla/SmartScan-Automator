import asyncio
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def run_and_save():

    try:
        from app.scrapers.n11 import N11Scraper
        from app.scrapers.teknosa import TeknosaScraper
        from app.scrapers.hepsiburada import HepsiburadaScraper
        from app.scrapers.vatanbilgisayar import VatanBilgisayarScraper
    except ImportError as e:
        print(f"Hata: Kütüphane veya dosya eksik! -> {e}")
        print("Lütfen 'pip install curl_cffi' yaptığından emin ol.")
        return

    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, 'test_data')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    scrapers = [
        N11Scraper(), 
        TeknosaScraper(), 
        HepsiburadaScraper(),
        VatanBilgisayarScraper()
    ]
    
    queries = ["iphone 15", "gaming laptop"] 

    for scraper in scrapers:
        site_name = scraper.__class__.__name__.replace("Scraper", "").lower()
        print(f"--- {site_name} verisi çekiliyor... ---")
        
        all_results = []
        for q in queries:
            try:
                print(f"'{q}' aranıyor...")
                res = await scraper.search(q)
                if res:
                    all_results.extend(res)
            except Exception as e:
                print(f"{site_name} hatası: {e}")
                continue

        file_path = os.path.join(output_dir, f"{site_name}_mock_data.json")
        with open(file_path, "w", encoding="utf-8") as f:
            formatted_data = []
            for item in all_results:
                formatted_data.append({
                    "title": getattr(item, 'name', 'N/A'),
                    "price": getattr(item, 'price', 'N/A'),
                    "link": getattr(item, 'url', 'N/A'),
                    "date": "2026-04-22"
                })
            json.dump(formatted_data, f, ensure_ascii=False, indent=4)
        print(f"Kaydedildi: {file_path} ({len(all_results)} ürün)")

if __name__ == "__main__":
    asyncio.run(run_and_save())