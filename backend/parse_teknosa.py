from bs4 import BeautifulSoup
import re

def main():
    # Az önce kaydettiğimiz HTML dosyasını okuyoruz
    with open("teknosa_debug.html", "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "lxml")
    
    # DİKKAT: "ul.prd > li > div.prd-inner" yerine 
    # sadece "div.prd-inner" diyerek kuralı esnetiyoruz!
    cards = soup.select("div.prd-inner")
    print(f"Toplam bulunan kart sayısı: {len(cards)}")

    for i, card in enumerate(cards[:5]): # İlk 5 ürünü test edelim
        name_el  = card.select_one("h3.prd-title")
        price_el = card.select_one("div.prd-prc2") or card.select_one("div.prd-prc1")
        link_el  = card.select_one("a.prd-link")

        print(f"\n--- Kart {i+1} ---")
        if name_el:
            # Senin koddaki boşluk problemini çözecek isim temizleme
            name_raw = name_el.get_text(separator=" ", strip=True)
            name_clean = " ".join(name_raw.split())
            print(f"  AD    : {name_clean}")
        else:
            print("  AD    : BULUNAMADI")

        if price_el:
            print(f"  FİYAT : {price_el.get_text(strip=True)}")
        else:
            print("  FİYAT : BULUNAMADI")
            
        if link_el:
            print(f"  URL   : {link_el.get('href', '')}")
        else:
            print("  URL   : BULUNAMADI")

if __name__ == "__main__":
    main()