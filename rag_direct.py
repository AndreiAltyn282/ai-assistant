import chromadb
import requests
import json

print("🔍 Подключение к ChromaDB...")
client = chromadb.HttpClient(host="127.0.0.1", port=8001)
collection = client.get_collection("default")
print(f"📚 Документов в базе: {collection.count()}")

query = "Что такое ИИ?"
print(f"🔍 Поиск по запросу: {query}")

# 1. Поиск в ChromaDB
results = collection.query(query_texts=[query], n_results=1)

if results['documents'] and len(results['documents'][0]) > 0:
    context = results['documents'][0][0]
    print(f"📚 Найден контекст: {context[:100]}...")
    
    # 2. Формируем промпт
    prompt = f"""Используя контекст, ответь на вопрос.

Контекст: {context}

Вопрос: {query}

Ответ:"""

    print("🤖 Отправка запроса в Ollama...")
    # 3. Отправляем в Ollama
    ollama_resp = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={"model": "mistral:7b-instruct-v0.3-q4_K_M", "prompt": prompt, "stream": False},
        timeout=120
    )
    
    answer = ollama_resp.json().get("response", "")
    print(f"🤖 Ответ: {answer}")
else:
    print("❌ Документы не найдены в ChromaDB")
