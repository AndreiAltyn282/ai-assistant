import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path

# === НАСТРОЙКИ ===
K8S_URL = "https://kubernetes.io/docs/home/"
OUTPUT_DIR = "rag_texts"

def fetch_kubernetes_docs():
    """Скачивает документацию Kubernetes"""
    print("📡 Загрузка документации Kubernetes...")
    
    try:
        response = requests.get(K8S_URL, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()
        
        # Сохраняем в файл
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        filepath = os.path.join(OUTPUT_DIR, "kubernetes_docs.txt")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=== Kubernetes Documentation ===\n\n")
            f.write(text)
        
        print(f"✅ Сохранено: {filepath}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    fetch_kubernetes_docs()
