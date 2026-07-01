import os
from pathlib import Path
from bs4 import BeautifulSoup

# === НАСТРОЙКИ ===
DJANGO_DIR = "django_docs"
OUTPUT_DIR = "rag_texts"

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def process_django_docs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = 0
    
    for html_path in Path(DJANGO_DIR).rglob('*.html'):
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            text = extract_text_from_html(content)
            if len(text.strip()) > 100:
                txt_path = os.path.join(OUTPUT_DIR, f"django_{html_path.stem}.txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                total += 1
                if total % 50 == 0:
                    print(f"  ✅ Обработано {total} файлов")
        except Exception as e:
            print(f"  ❌ Ошибка {html_path.name}: {e}")
    
    print(f"\n✅ Обработано {total} Django-файлов")

if __name__ == "__main__":
    process_django_docs()
