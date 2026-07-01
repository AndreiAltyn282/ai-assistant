import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# === НАСТРОЙКИ ===
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"

# === ЗАГРУЗКА ТЕКСТОВЫХ ФАЙЛОВ ===
def load_text_files(directory):
    docs = []
    metadatas = []
    
    if not os.path.exists(directory):
        print(f"  ⚠️ Папка {directory} не найдена, пропускаем")
        return docs, metadatas
    
    for filepath in Path(directory).rglob('*.txt'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                docs.append(content)
                metadatas.append({"source": str(filepath), "type": "text"})
                print(f"  ✅ Загружен: {filepath.name}")
        except Exception as e:
            print(f"  ❌ Ошибка {filepath.name}: {e}")
    
    return docs, metadatas

# === ЗАГРУЗКА HTML-ФАЙЛОВ ===
def load_html_files(directory):
    from bs4 import BeautifulSoup
    docs = []
    metadatas = []
    
    if not os.path.exists(directory):
        print(f"  ⚠️ Папка {directory} не найдена, пропускаем")
        return docs, metadatas
    
    for filepath in Path(directory).rglob('*.html'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
                text = soup.get_text()
                docs.append(text)
                metadatas.append({"source": str(filepath), "type": "html"})
                print(f"  ✅ Загружен: {filepath.name}")
        except Exception as e:
            print(f"  ❌ Ошибка {filepath.name}: {e}")
    
    return docs, metadatas

# === ЗАГРУЗКА КОДА PYTHON ===
def load_python_files(directory):
    docs = []
    metadatas = []
    
    if not os.path.exists(directory):
        print(f"  ⚠️ Папка {directory} не найдена, пропускаем")
        return docs, metadatas
    
    for filepath in Path(directory).rglob('*.py'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                docs.append(content)
                metadatas.append({"source": str(filepath), "type": "python"})
                print(f"  ✅ Загружен: {filepath.name}")
        except Exception as e:
            print(f"  ❌ Ошибка {filepath.name}: {e}")
    
    return docs, metadatas

# === СОХРАНЕНИЕ В CHROMADB ===
def save_to_chromadb(docs, metadatas):
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client.get_collection(COLLECTION_NAME)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", ", ", " "]
    )
    
    all_chunks = []
    all_metadatas = []
    
    for doc, meta in zip(docs, metadatas):
        chunks = splitter.split_text(doc)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            meta_copy = meta.copy()
            meta_copy["chunk_index"] = i
            all_metadatas.append(meta_copy)
    
    if all_chunks:
        # Добавляем батчами по 100
        for i in range(0, len(all_chunks), 100):
            batch_chunks = all_chunks[i:i+100]
            batch_metadatas = all_metadatas[i:i+100]
            batch_ids = [f"doc_{j}" for j in range(i, i+len(batch_chunks))]
            collection.add(
                documents=batch_chunks,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
            print(f"  Добавлено {len(batch_chunks)} чанков")
    
    return len(all_chunks)

# === ГЛАВНАЯ ===
def main():
    print("📚 Загрузка всех документов в базу знаний...")
    print("="*60)
    
    all_docs = []
    all_metadatas = []
    
    # 1. Текстовые файлы из docs/
    print("\n📄 Загрузка текстовых файлов...")
    docs, metas = load_text_files("docs")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    # 2. Книги
    print("\n📚 Загрузка книг...")
    docs, metas = load_text_files("books")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    # 3. Django docs
    print("\n🌐 Загрузка Django документации...")
    docs, metas = load_html_files("django_docs")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    # 4. FastAPI docs
    print("\n🌐 Загрузка FastAPI документации...")
    docs, metas = load_html_files("fastapi_docs")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    # 5. GitHub репозитории
    print("\n🐙 Загрузка GitHub репозиториев...")
    docs, metas = load_python_files("github_repos")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    # 6. Твои скрипты
    print("\n📁 Загрузка твоих скриптов...")
    docs, metas = load_python_files("my_scripts")
    all_docs.extend(docs)
    all_metadatas.extend(metas)
    
    print("\n" + "="*60)
    print(f"✅ Всего загружено: {len(all_docs)} документов")
    
    if all_docs:
        count = save_to_chromadb(all_docs, all_metadatas)
        print(f"✅ Сохранено {count} чанков в ChromaDB")
    
    print("\n📊 ИТОГО:")
    print(f"  Документов: {len(all_docs)}")
    if all_docs:
        print(f"  Чанков: {count}")

if __name__ == "__main__":
    main()
