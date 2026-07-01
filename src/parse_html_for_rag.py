import os
import sys
from bs4 import BeautifulSoup
from pathlib import Path

# === НАСТРОЙКИ ===
HTML_DIR = "rag_docs"  # Теперь здесь все HTML-файлы по категориям
OUTPUT_DIR = "rag_texts"

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
    
    for html_path in Path(HTML_DIR).rglob('*.html'):
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            text = extract_text_from_html(html_content)
            if len(text.strip()) > 100:
                # Сохраняем с путём, чтобы видеть категорию
                rel_path = html_path.relative_to(HTML_DIR)
                txt_path = os.path.join(OUTPUT_DIR, str(rel_path).replace('/', '_').replace('.html', '.txt'))
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f'✅ {rel_path} -> {txt_path}')
        except Exception as e:
            print(f'❌ Ошибка {html_path}: {e}')

if __name__ == "__main__":
    process_html_files()
