import os
import sys
from bs4 import BeautifulSoup
from pathlib import Path

# === НАСТРОЙКИ ===
RAG_DIR = "rag_docs"
OUTPUT_DIR = "rag_texts"

def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for script in soup(["script", "style", "nav", "header", "footer"]):
        script.decompose()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)

def process_all_docs():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total_processed = 0
    
    for file_path in Path(RAG_DIR).rglob('*'):
        if file_path.suffix in ['.html', '.txt']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if file_path.suffix == '.html':
                    text = extract_text_from_html(content)
                else:
                    text = content
                
                if len(text.strip()) > 100:
                    txt_path = os.path.join(OUTPUT_DIR, file_path.stem + '.txt')
                    with open(txt_path, 'w', encoding='utf-8') as f:
                        f.write(text)
                    total_processed += 1
                    if total_processed % 10 == 0:
                        print(f"  ✅ Обработано {total_processed} файлов")
            except Exception as e:
                print(f"  ❌ Ошибка {file_path.name}: {e}")
    
    print(f"\n✅ Обработано {total_processed} файлов")
    print(f"✅ Сохранено в: {OUTPUT_DIR}/")

if __name__ == "__main__":
    process_all_docs()
