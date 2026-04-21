import asyncio
from bs4 import BeautifulSoup

async def main():
    try:
        with open("n11_discovery.html", "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("HATA: n11_discovery.html bulunamadı! Önce keşif kodunu çalıştır.")
        return

    soup = BeautifulSoup(content, "lxml")

    print("=== .product-item Yapı Analizi ===")
    items = soup.select(".product-item")
    print(f"Tespit edilen toplam ürün kartı (.product-item): {len(items)}")

    if items:
        # İlk 3 ürünü inceleyelim
        for i, item in enumerate(items[:3]):
            print(f"\n--- ÜRÜN #{i+1} ---")
            
            # Başlık Analizi
            name_el = item.select_one(".product-item-title")
            if name_el:
                print(f"  AD (Class: .product-item-title): {name_el.get_text(strip=True)[:70]}...")
                # Vatan'daki gibi üst etiketlere bakalım
                print(f"  Adın Parent Tag: {name_el.parent.name}, Parent Class: {name_el.parent.get('class')}")
            
            # Fiyat Analizi
            price_el = item.select_one(".price") or item.select_one(".basket-price")
            if price_el:
                print(f"  FİYAT (Class: {price_el.get('class')}): {price_el.get_text(strip=True)}")
                
            # Link ve Resim Analizi
            link_el = item.select_one("a")
            img_el = item.select_one("img")
            
            if link_el:
                print(f"  LINK Tag: {link_el.name}, Href: {link_el.get('href', '')[:50]}...")
            if img_el:
                print(f"  RESİM Tag: {img_el.name}, Src/Data-src: {img_el.get('data-original', img_el.get('src', ''))[:50]}...")

    else:
        print("\n!!! KRİTİK HATA: .product-item bulundu ama içi boş gözüküyor.")
        # Alternatif kapsayıcıyı kontrol edelim
        alt_items = soup.select("li.column")
        print(f"Alternatif (li.column) sayısı: {len(alt_items)}")

if __name__ == "__main__":
    asyncio.run(main())