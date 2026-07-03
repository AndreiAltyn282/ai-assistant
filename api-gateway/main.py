import httpx
import os
import chromadb
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# ========== КОНФИГУРАЦИЯ ==========
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
CHROMADB_HOST = os.getenv("CHROMADB_HOST", "127.0.0.1")
CHROMADB_PORT = int(os.getenv("CHROMADB_PORT", "8001"))
MODEL_RAG = os.getenv("MODEL_RAG", "mistral:7b-instruct-v0.3-q4_K_M")

# ========== ПОДКЛЮЧЕНИЕ К CHROMADB (ЧЕРЕЗ БИБЛИОТЕКУ) ==========
print("🔍 Подключение к ChromaDB...")
chroma_client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

# Проверяем или создаём коллекцию
try:
    collection = chroma_client.get_collection("default")
    print(f"✅ Коллекция найдена, документов: {collection.count()}")
except:
    print("📚 Создаём новую коллекцию...")
    collection = chroma_client.create_collection("default")
    # Добавляем тестовый документ
    collection.add(
        ids=["doc1"],
        documents=["Искусственный интеллект (ИИ) — это область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, требующие человеческого интеллекта."]
    )
    print(f"✅ Коллекция создана, документов: {collection.count()}")

# ========== МОДЕЛИ ДАННЫХ ==========
class QueryRequest(BaseModel):
    query: str
    model: Optional[str] = None
    use_rag: Optional[bool] = True
    top_k: Optional[int] = 3

# ========== ПРИЛОЖЕНИЕ ==========
app = FastAPI(title="AI Assistant API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = httpx.AsyncClient(timeout=120.0)

# ========== ЭНДПОИНТЫ ==========

@app.get("/health")
async def health():
    status = {"status": "healthy", "services": {"ollama": False, "chromadb": False}}
    try:
        resp = await client.get(f"{OLLAMA_URL}/api/tags")
        status["services"]["ollama"] = resp.status_code == 200
    except:
        pass
    try:
        collection.count()
        status["services"]["chromadb"] = True
    except:
        pass
    return status

@app.post("/api/rag")
async def rag_query(request: QueryRequest):
    try:
        model = request.model or MODEL_RAG
        chroma_results = []
        
        print(f"\n🔍 ЗАПРОС: {request.query}")
        print(f"🔍 USE_RAG: {request.use_rag}")
        
        # ====== ПОИСК В CHROMADB (ЧЕРЕЗ БИБЛИОТЕКУ) ======
        if request.use_rag:
            try:
                print("🔍 Поиск в ChromaDB через библиотеку...")
                results = collection.query(
                    query_texts=[request.query],
                    n_results=request.top_k
                )
                print(f"🔍 Результаты: {results}")
                
                if results['documents'] and len(results['documents'][0]) > 0:
                    for i, doc in enumerate(results['documents'][0]):
                        chroma_results.append({
                            "id": results['ids'][0][i],
                            "document": doc
                        })
                    print(f"✅ Найдено документов: {len(chroma_results)}")
                else:
                    print("⚠️ Документы не найдены")
                    
            except Exception as e:
                print(f"⚠️ ChromaDB ошибка: {e}")
        else:
            print("🔍 RAG отключён")
        
        # ====== ФОРМИРУЕМ ПРОМПТ ======
        if request.use_rag and chroma_results:
            context = "\n\n".join([d["document"] for d in chroma_results])
            prompt = f"""Используя контекст, ответь на вопрос.

Контекст:
{context}

Вопрос: {request.query}

Ответ:"""
            print(f"🔍 Используем контекст (документов: {len(chroma_results)})")
        else:
            prompt = request.query
            print("🔍 Без контекста")
        
        # ====== ОТПРАВКА В OLLAMA ======
        print(f"🤖 Запрос к Ollama. Модель: {model}")
        ollama_resp = await client.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False}
        )
        
        if ollama_resp.status_code != 200:
            raise HTTPException(status_code=500, detail="Ollama error")
        
        result = {
            "query": request.query,
            "answer": ollama_resp.json().get("response", ""),
            "model": model,
            "use_rag": request.use_rag,
            "context": chroma_results if request.use_rag else []
        }
        
        print("✅ Ответ отправлен")
        return result
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ollama/models")
async def get_ollama_models():
    try:
        resp = await client.get(f"{OLLAMA_URL}/api/tags")
        return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
