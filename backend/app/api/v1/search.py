from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.scrapers import ALL_SCRAPERS
import asyncio
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search")
async def search_products(
    q: str = "",
    limit: Optional[str] = "500",
    db: AsyncSession = Depends(get_db)
):
    try:
        limit_int = int(limit) if limit and limit.strip() else 500
    except ValueError:
        limit_int = 500

    q = q.strip()
    if not q:
        return {"query": q, "results": [], "count": 0}

    tasks = [scraper.search(q) for scraper in ALL_SCRAPERS]
    all_results = await asyncio.gather(*tasks, return_exceptions=False)

    results = []
    for site_results in all_results:
        if isinstance(site_results, list):
            results.extend(site_results)

    search_terms = q.lower().split()
    filtered_results = []
    for r in results:
        name_lower = r.name.lower()
        if all(term in name_lower for term in search_terms):
            filtered_results.append(r)
    results = filtered_results

    results.sort(key=lambda x: x.price)

    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "site": r.site,
                "name": r.name,
                "price": r.price,
                "original_price": r.original_price,
                "url": r.url,
                "image_url": r.image_url,
                "in_stock": r.in_stock,
            }
            for r in results[:limit_int]
        ]
    }