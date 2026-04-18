from fastapi import APIRouter
from app.scrapers import ALL_SCRAPERS
import asyncio

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search")
async def search_products(q: str = "", limit: int = 20):
    if not q:
        return {"query": q, "results": [], "count": 0}

    # Tüm scraper'ları aynı anda çalıştır
    tasks = [scraper.search(q) for scraper in ALL_SCRAPERS]
    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    for site_results in all_results:
        if isinstance(site_results, list):
            results.extend(site_results)

    # Fiyata göre sırala
    results.sort(key=lambda x: x.price)

    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "site": r.site,
                "name": r.name,
                "price": r.price,
                "url": r.url,
                "image_url": r.image_url,
                "in_stock": r.in_stock,
            }
            for r in results[:limit]
        ]
    }