from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.product import Product
from app.models.price import Price
from app.scrapers import ALL_SCRAPERS
import asyncio
import re  # BİZİM YENİ SÜPER SİLAHIMIZ (REGEX)

router = APIRouter(prefix="/api/v1", tags=["search"])

@router.get("/search")
async def search_products(
    q: str = "",
    limit: int = 60,
    db: AsyncSession = Depends(get_db)
):
    if not q.strip():
        return {"query": q, "results": [], "count": 0}

    tasks = [scraper.search(q) for scraper in ALL_SCRAPERS]
    all_results = await asyncio.gather(*tasks, return_exceptions=False)

    results = []
    for site_results in all_results:
        if isinstance(site_results, list):
            results.extend(site_results)

    # --- SÜPER AKILLI FİLTRE BAŞLIYOR ---
    search_terms = q.lower().split() 
    filtered_results = []
    
    for r in results:
        name_lower = r.name.lower()
        # Kelimenin önüne ve arkasına \b (kelime sınırı) koyarak "tam eşleşme" arıyoruz
        if all(re.search(rf"\b{re.escape(term)}\b", name_lower) for term in search_terms):
            filtered_results.append(r)
            
    results = filtered_results
    # --- FİLTRE BİTTİ ---

    results.sort(key=lambda x: x.price)

    for r in results:
        stmt = select(Product).where(Product.name == r.name)
        existing = await db.execute(stmt)
        product = existing.scalar_one_or_none()

        if not product:
            product = Product(
                name=r.name,
                image_url=r.image_url,
            )
            db.add(product)
            await db.flush()

        price_record = Price(
            product_id=product.id,
            site=r.site,
            price=r.price,
            original_price=r.original_price,
            url=r.url,
            image_url=r.image_url,
            in_stock=r.in_stock,
        )
        db.add(price_record)

    await db.commit()

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
            for r in results[:limit]
        ]
    }