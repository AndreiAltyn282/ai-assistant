import streamlit as st
import chromadb
import ollama

# === НАСТРОЙКИ ===
MODEL_NAME = "deepseek-coder:6.7b-instruct-q4_K_M"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "python_docs"

# === НАСТРОЙКА СТРАНИЦЫ ===
st.set_page_config(
    page_title="🧠 AI-помощник для программистов",
    page_icon="🧠",
    layout="wide"
)

# === ПОДКЛЮЧЕНИЕ К CHROMADB ===
@st.cache_resource
def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_collection(COLLECTION_NAME)

# === ПОИСК ===
def search(query, collection, n_results=5):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results['documents'][0], results['metadatas'][0], results['distances'][0]

# === ГЕНЕРАЦИЯ ===
def generate_response(query, context, model_name=MODEL_NAME):
    prompt = f"""Ты — профессиональный AI-ассистент для программистов.
Твоя задача — отвечать на вопросы, используя предоставленный контекст.

=== КОНТЕКСТ ===
{context}

=== ВОПРОС ===
{query}

=== ОТВЕТ ===
Дай точный, полезный и структурированный ответ. Если в контексте нет информации — скажи об этом честно.
"""
    
    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": "Ты эксперт по программированию. Отвечай точно и по делу."},
                {"role": "user", "content": prompt}
            ],
            options={"temperature": 0.3, "num_predict": 1500}
        )
        return response['message']['content']
    except Exception as e:
        return f"❌ Ошибка: {e}"

# === ИНТЕРФЕЙС ===
st.title("🧠 AI-помощник для программистов")
st.markdown("Использует **DeepSeek-Coder** и базу знаний.")

# Боковая панель
with st.sidebar:
    st.header("⚙️ Настройки")
    
    model_options = ["deepseek-coder:6.7b-instruct-q4_K_M", "llama3.2:3b", "qwen2.5:7b"]
    selected_model = st.selectbox("Модель:", model_options, index=0)
    
    n_results = st.slider("Количество источников:", min_value=1, max_value=10, value=5)
    
    st.divider()
    
    try:
        collection = get_collection()
        st.metric("📚 Документов в базе", collection.count())
    except Exception as e:
        st.error(f"❌ Ошибка подключения к ChromaDB: {e}")
    
    st.divider()
    
    if st.button("🗑️ Очистить историю"):
        st.session_state.messages = []
        st.rerun()

# История
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "source" in msg and msg["source"]:
            with st.expander("📚 Показать источники"):
                for src in msg["source"]:
                    st.caption(f"📄 {src}")

# Поле ввода
if prompt := st.chat_input("Введите вопрос по программированию..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "source": None})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🔍 Поиск в базе знаний..."):
            try:
                collection = get_collection()
                docs, metadatas, distances = search(prompt, collection, n_results)
                
                context = "\n\n---\n\n".join(docs)
                sources = [f"{meta.get('source', 'unknown')}" for meta in metadatas]
                
                with st.spinner("🤖 Генерация ответа..."):
                    answer = generate_response(prompt, context, selected_model)
                
                st.markdown(answer)
                
                with st.expander("📚 Показать источники"):
                    for i, source in enumerate(sources):
                        st.caption(f"📄 {source}")
                        st.caption(f"📊 Релевантность: {1 - distances[i]:.2f}")
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "source": sources
                })
                
            except Exception as e:
                st.error(f"❌ Ошибка: {e}")

st.divider()
st.caption("🚀 AI Assistant | Сделано с ❤️")
