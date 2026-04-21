from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.product import Product
from app.models.price import Price
from app.scrapers import ALL_SCRAPERS
import asyncio
import re
from typing import Optional

router = APIRouter(prefix="/api/v1", tags=["search"])

# --- YENİ SÜPER SİLAHIMIZ: KELİME ATOMİZERİ (TOKENIZER) ---
def tokenize_text(text: str) -> set:
    # 1. Noktalama işaretlerini (", ', -, vs.) boşluğa çevir
    t = re.sub(r'[^\w\s]', ' ', text)
    # 2. Harf ve rakam arasına kılıç gibi gir (Örn: A11 -> A 11, RTX4060 -> RTX 4060)
    t = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', t)
    t = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', t)
    # 3. Kelimeleri tek tek koparıp bir kümeye (set) at
    return set(t.lower().split())
# -----------------------------------------------------------

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

    # --- SÜPER KUSURSUZ FİLTRE BAŞLIYOR ---
    # Aranan kelimeleri atomlarına ayır (Örn "s11 tablet" -> {'s', '11', 'tablet'})
    search_tokens = tokenize_text(q)
    filtered_results = []
    
    for r in results:
        # Ürün adını atomlarına ayır
        product_tokens = tokenize_text(r.name)
        
        # Eğer aradığımız tüm atomlar (s, 11, tablet), ürünün atomları içinde bağımsız olarak varsa:
        if search_tokens.issubset(product_tokens):
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
            for r in results[:limit_int]
        ]
    }