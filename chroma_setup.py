import chromadb
from chromadb.utils import embedding_functions
import time

# Подключаемся к ChromaDB
client = chromadb.HttpClient(host="127.0.0.1", port=8001)

# Удаляем старую коллекцию, если есть
try:
    client.delete_collection("default")
    print("🗑️ Старая коллекция удалена")
except:
    print("ℹ️ Коллекции не было, создаём новую")

# Создаём коллекцию
collection = client.create_collection(name="default")

# Добавляем документы
collection.add(
    ids=["doc1"],
    documents=["Искусственный интеллект (ИИ) — это область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, требующие человеческого интеллекта."]
)

# Проверяем количество
count = collection.count()
print(f"✅ Документов в коллекции: {count}")

# Тестируем поиск (без эмбеддингов, просто для проверки)
results = collection.query(
    query_texts=["Что такое ИИ?"],
    n_results=1
)

print("✅ Результаты поиска:")
print(f"   Найденные ID: {results['ids']}")
print(f"   Найденные документы: {results['documents']}")
