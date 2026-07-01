import os
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions

# === НАСТРОЙКИ ===
DOCS_DIR = "rag_texts"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"

def load_documents():
    docs = []
    filenames = []
    
    if not os.path.exists(DOCS_DIR):
        print(f"❌ Папка {DOCS_DIR} не найдена!")
        return docs, filenames
    
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                docs.append(f.read())
                filenames.append(filename)
    
    return docs, filenames

def split_documents(docs, filenames):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    
    all_chunks = []
    all_metadatas = []
    
    for doc, filename in zip(docs, filenames):
        chunks = splitter.split_text(doc)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({"source": filename, "chunk_index": i})
    
    return all_chunks, all_metadatas

def create_and_store_embeddings(chunks, metadatas):
    if len(chunks) == 0:
        print("❌ Нет данных для векторизации!")
        return None
    
    print(f"🔢 Создание эмбеддингов для {len(chunks)} чанков...")
    
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks, show_progress_bar=True)
    
    print(f"✅ Создано {len(embeddings)} эмбеддингов")
    
    print("💾 Сохранение в ChromaDB...")
    
    chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)
    
    try:
        chroma_client.delete_collection(COLLECTION_NAME)
        print("🗑️ Старая коллекция удалена")
    except:
        pass
    
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name='all-MiniLM-L6-v2'
        )
    )
    
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch_chunks = chunks[i:i+batch_size]
        batch_metadatas = metadatas[i:i+batch_size]
        batch_ids = [f"doc_{j}" for j in range(i, i+len(batch_chunks))]
        
        collection.add(
            documents=batch_chunks,
            metadatas=batch_metadatas,
            ids=batch_ids
        )
        print(f"  Добавлено {len(batch_chunks)} чанков")
    
    print(f"✅ Сохранено {collection.count()} документов в ChromaDB")
    return collection

def main():
    print("📚 Загрузка документов...")
    docs, filenames = load_documents()
    print(f"✅ Загружено {len(docs)} документов")
    
    if len(docs) == 0:
        print("❌ Нет документов! Добавьте .txt файлы в папку rag_texts/")
        return
    
    print("✂️ Разбивка на чанки...")
    chunks, metadatas = split_documents(docs, filenames)
    print(f"✅ Создано {len(chunks)} чанков")
    
    if len(chunks) == 0:
        print("❌ Нет чанков для векторизации!")
        return
    
    collection = create_and_store_embeddings(chunks, metadatas)
    
    if collection:
        print(f"\n🔍 Тест поиска:")
        test_query = "Что такое Django?"
        results = collection.query(query_texts=[test_query], n_results=3)
        
        print(f"Вопрос: {test_query}")
        if results['documents'] and results['documents'][0]:
            print("Результаты:")
            for i, doc in enumerate(results['documents'][0]):
                print(f"  {i+1}. {doc[:150]}...")

if __name__ == "__main__":
    main()
