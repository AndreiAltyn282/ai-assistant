import chromadb
import ollama

# === НАСТРОЙКИ ===
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"

# === ПОДКЛЮЧЕНИЕ К CHROMADB ===
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)

# === ПОИСК В БАЗЕ ===
def search(query, collection, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results['documents'][0], results['metadatas'][0]

# === ГЕНЕРАЦИЯ ОТВЕТА ===
def generate_response(query, context):
    prompt = f"""Ты — AI-помощник для программистов.
Ответь на вопрос, используя контекст ниже.

Контекст:
{context}

Вопрос: {query}

Ответ:"""
    
    response = ollama.chat(model=MODEL_NAME, messages=[
        {"role": "system", "content": "Ты эксперт по Python и программированию."},
        {"role": "user", "content": prompt}
    ])
    return response['message']['content']

# === ГЛАВНАЯ ФУНКЦИЯ ===
def main():
    print("🔗 Подключение к ChromaDB...")
    collection = get_collection()
    print(f"✅ Загружено {collection.count()} документов")
    
    while True:
        query = input("\n❓ Введите вопрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break
        
        print("🔍 Поиск в базе знаний...")
        docs, metadatas = search(query, collection)
        context_text = "\n\n".join(docs)
        
        print("🤖 Генерация ответа...")
        answer = generate_response(query, context_text)
        print("\n" + "="*50)
        print(answer)
        print("="*50)

if __name__ == "__main__":
    main()
