import chromadb

print("🔍 Подключение к ChromaDB...")
client = chromadb.HttpClient(host="127.0.0.1", port=8001)

# Удаляем старую коллекцию, если есть
try:
    client.delete_collection("default")
    print("🗑️ Старая коллекция удалена")
except:
    print("ℹ️ Коллекции не было")

# Создаём новую коллекцию
print("📚 Создаём новую коллекцию...")
collection = client.create_collection(
    name="default",
    metadata={"hnsw:space": "cosine"}
)

# Добавляем документ
print("📝 Добавляем документ...")
collection.add(
    ids=["doc1"],
    documents=["Искусственный интеллект (ИИ) — это область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, требующие человеческого интеллекта."]
)

print(f"✅ Коллекция создана, документов: {collection.count()}")
print("🎉 ChromaDB готов к работе!")
