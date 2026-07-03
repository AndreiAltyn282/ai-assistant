import chromadb
import ollama
from datetime import datetime

# === НАСТРОЙКИ ===
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"

# === СЦЕНАРИИ ОТВЕТОВ ===
def get_scenario(query):
    """Выбирает сценарий по теме вопроса"""
    query_lower = query.lower()
    if "код" in query_lower or "python" in query_lower or "напиши" in query_lower:
        return """
1. Определи, что нужно сделать.
2. Напиши готовый код с комментариями.
3. Объясни, как это работает.
"""
    elif "что такое" in query_lower or "объясни" in query_lower or "как работает" in query_lower:
        return """
1. Объясни простыми словами.
2. Приведи пример использования.
3. Скажи, где это применяется.
"""
    else:
        return """
1. Кратко опиши суть.
2. Выдели главное.
3. Дай практическую рекомендацию.
"""

# === ПОДКЛЮЧЕНИЕ К CHROMADB ===
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)

# === ПОИСК В БАЗЕ ===
def search(query, collection, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results['documents'][0], results['metadatas'][0], results['distances'][0]

# === ГЕНЕРАЦИЯ ОТВЕТА ===
def generate_response(query, context, model_name=MODEL_NAME):
    scenario = get_scenario(query)
    
    prompt = f"""Ты — профессиональный AI-ассистент для программистов.
Отвечай строго по сценарию:

{scenario}

=== КОНТЕКСТ ИЗ ДОКУМЕНТАЦИИ ===
{context}

=== ВОПРОС ПОЛЬЗОВАТЕЛЯ ===
{query}

=== ОТВЕТ ===
"""
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты — AI-ассистент. Отвечай строго по сценарию."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.3,
                "num_predict": 1500,
            }
        )
        return response['message']['content']
    except Exception as e:
        return f"❌ Ошибка генерации: {e}"

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    print("🚀 RAG-помощник для программистов")
    print("="*60)
    print(f"📚 База знаний: {CHROMA_DIR}")
    print("="*60)
    
    try:
        collection = get_collection()
        print(f"✅ Загружено {collection.count()} документов")
    except Exception as e:
        print(f"❌ Ошибка подключения к ChromaDB: {e}")
        return
    
    # Проверка Ollama
    try:
        ollama.list()
        print("✅ Ollama доступен")
    except Exception:
        print("⚠️ Ollama не отвечает! Запусти: ollama serve &")
    
    print("\n" + "="*60)
    print("💬 Вводи вопросы, /exit для выхода")
    print("="*60)
    
    history = []
    
    while True:
        query = input("\n❓ Вопрос: ").strip()
        
        if not query:
            continue
        
        if query.lower() == '/exit':
            print("👋 До свидания!")
            break
        
        if query.lower() == '/history':
            if not history:
                print("📭 История пуста")
            else:
                print("\n📜 ИСТОРИЯ (последние 5):")
                for i, item in enumerate(history[-5:], 1):
                    print(f"{i}. {item['query'][:50]}... ({item['timestamp'][:16]})")
            continue
        
        print("🔍 Поиск в базе знаний...")
        docs, metadatas, distances = search(query, collection, n_results=3)
        context = "\n\n---\n\n".join(docs)
        
        print("🤖 Генерация ответа...")
        answer = generate_response(query, context)
        
        print("\n" + "="*60)
        print("🤖 ОТВЕТ:")
        print("="*60)
        print(answer)
        print("\n" + "="*60)
        print("📚 ИСТОЧНИКИ:")
        for i, meta in enumerate(metadatas):
            print(f"  {i+1}. {meta.get('source', 'unknown')} (релевантность: {1 - distances[i]:.2f})")
        print("="*60)
        
        history.append({
            "query": query,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    main()
