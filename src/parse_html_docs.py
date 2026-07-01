import os
import sys
from bs4 import BeautifulSoup
from pathlib import Path

# === НАСТРОЙКИ ===
HTML_DIR = "python_html_docs"  # <-- ИЗМЕНЕНО!
OUTPUT_DIR = "rag_texts"       # <-- ИЗМЕНЕНО!

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def process_html_files():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    html_files = list(Path(HTML_DIR).rglob('*.html'))
    print(f"📁 Найдено {len(html_files)} HTML-файлов")
    
    total_processed = 0
    for html_path in html_files:
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            text = extract_text_from_html(html_content)
            if len(text.strip()) > 100:
                txt_path = os.path.join(OUTPUT_DIR, html_path.stem + '.txt')
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                total_processed += 1
                if total_processed % 50 == 0:
                    print(f"  ✅ Обработано {total_processed} файлов")
        except Exception as e:
            print(f"  ❌ Ошибка {html_path.name}: {e}")
    
    print(f"\n✅ Обработано {total_processed} HTML-файлов")
    print(f"✅ Сохранено в: {OUTPUT_DIR}/")

if __name__ == "__main__":
    process_html_files()
