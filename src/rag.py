import os
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter  # <-- ИСПРАВЛЕНО!
import ollama
from sklearn.metrics.pairwise import cosine_similarity

# === НАСТРОЙКИ ===
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"
DOCS_DIR = "docs"

# === 1. ЗАГРУЗКА ДОКУМЕНТОВ ===
def load_documents():
    docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".txt"):
            with open(os.path.join(DOCS_DIR, filename), "r", encoding="utf-8") as f:
                docs.append(f.read())
    return "\n\n".join(docs)

# === 2. РАЗБИВКА НА ЧАНКИ (БЕЗ "*") ===
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=[
            "\n\n",      # Абзацы
            "\n",        # Строки
            ". ",        # Предложения
            ", ",        # Части предложений
            " "          # Слова (в крайнем случае)
        ]
    )
    return splitter.split_text(text)

# === 3. СОЗДАНИЕ ЭМБЕДДИНГОВ ===
def create_embeddings(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks)
    return embeddings

# === 4. ПОИСК В ВЕКТОРНОЙ БАЗЕ ===
def search(query, chunks, embeddings):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings)[0]
    top_indices = similarities.argsort()[-3:][::-1]
    return [chunks[i] for i in top_indices]

# === 5. ГЕНЕРАЦИЯ ОТВЕТА ===
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
    print("📚 Загрузка документов...")
    text = load_documents()
    
    print("✂️ Разбивка на чанки...")
    chunks = split_text(text)
    print(f"✅ Создано {len(chunks)} чанков")
    
    print("🔢 Создание эмбеддингов...")
    embeddings = create_embeddings(chunks)
    
    while True:
        query = input("\n❓ Введите вопрос (или 'exit' для выхода): ")
        if query.lower() == 'exit':
            break
        
        print("🔍 Поиск в базе знаний...")
        context = search(query, chunks, embeddings)
        context_text = "\n\n".join(context)
        
        print("🤖 Генерация ответа...")
        answer = generate_response(query, context_text)
        print("\n" + "="*50)
        print(answer)
        print("="*50)

if __name__ == "__main__":
    main()
