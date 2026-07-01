import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

OUTPUT_DIR = "rag_texts"
BASE_URL = "https://kubernetes.io/docs/"
PAGES = [
    "home/",
    "concepts/",
    "tasks/",
    "reference/",
]

def fetch_page(url):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Удаляем скрипты и стили
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        
        return soup.get_text()
    except:
        return ""

def fetch_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_text = "=== Kubernetes Documentation ===\n\n"
    
    for page in PAGES:
        url = BASE_URL + page
        print(f"📡 Загрузка: {url}")
        text = fetch_page(url)
        all_text += f"\n\n--- {page} ---\n\n{text}"
        time.sleep(1)  # Пауза, чтобы не перегружать сайт
    
    filepath = os.path.join(OUTPUT_DIR, "kubernetes_full.txt")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(all_text)
    
    print(f"✅ Сохранено: {filepath}")

if __name__ == "__main__":
    fetch_all()
