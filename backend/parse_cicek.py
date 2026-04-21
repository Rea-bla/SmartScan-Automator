import bs4
from bs4 import BeautifulSoup

def main():
    with open("cicek_debug.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    soup = BeautifulSoup(content, "lxml")
    container = soup.select_one(".listing__products")
    
    if container:
        children = [c for c in container.children if isinstance(c, bs4.Tag)]
        if children:
            first = children[0]
            # İlk kartın içindeki tüm HTML'i düzenli bir şekilde yazdırıyoruz
            print(first.prettify())

if __name__ == "__main__":
    main()